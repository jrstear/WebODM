import os
import tempfile
from pathlib import Path

from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from app.models import Task


class GenerateGCPView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk, project__owner=request.user)

        emlid_file = request.FILES.get('emlid_csv')
        if emlid_file is None:
            return Response({'error': 'emlid_csv file is required'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Write uploaded CSV to a temp file
        with tempfile.NamedTemporaryFile(
                suffix='.csv', delete=False, mode='wb') as tmp:
            for chunk in emlid_file.chunks():
                tmp.write(chunk)
            tmp_csv_path = tmp.name

        try:
            # Resolve task paths
            images_dir = str(task.task_path("images"))

            # Find reconstruction.json if requested
            reconstruction_path = None
            use_recon = request.data.get('use_reconstruction', 'true')
            if use_recon in ('true', True, '1', 1):
                candidate = str(task.assets_path("opensfm", "reconstruction.json"))
                if os.path.exists(candidate):
                    reconstruction_path = candidate

            # Run pipeline synchronously
            from .pipeline import run_pipeline
            gcpeditpro_txt, estimates_json = run_pipeline(
                images_dir=images_dir,
                emlid_csv_path=tmp_csv_path,
                reconstruction_path=reconstruction_path,
            )

            # Write outputs to task assets directory
            out_dir = Path(str(task.assets_path()))
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / 'gcpeditpro.txt').write_text(gcpeditpro_txt)
            (out_dir / 'gcpeditpro.estimates.json').write_text(estimates_json)

        except Exception as e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            try:
                os.unlink(tmp_csv_path)
            except OSError:
                pass

        return Response({
            'gcpeditpro_txt': '/api/plugins/auto-gcp/task/{}/download/gcpeditpro.txt'.format(pk),
            'estimates_json': '/api/plugins/auto-gcp/task/{}/download/gcpeditpro.estimates.json'.format(pk),
        })


class DownloadGCPView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, filename):
        task = get_object_or_404(Task, pk=pk, project__owner=request.user)

        # Restrict to known safe filenames
        allowed = {'gcpeditpro.txt', 'gcpeditpro.estimates.json'}
        if filename not in allowed:
            raise Http404

        file_path = Path(str(task.assets_path(filename)))
        if not file_path.exists():
            raise Http404

        return FileResponse(
            open(file_path, 'rb'),
            as_attachment=True,
            filename=filename,
        )
