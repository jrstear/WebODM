from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def LoadButtonView(plugin):
    @login_required
    def view(request):
        return render(
            request,
            plugin.template_path("load_buttons.js"),
            {
                "app_name": plugin.get_name(),
                "api_url": plugin.public_url("").rstrip("/"),
            },
            content_type="text/javascript",
        )
    return view
