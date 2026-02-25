import React, { Component } from "react";

export default class TaskView extends Component {
    state = {
        showModal: false,
        loading: false,
        error: null,
        result: null,
        useReconstruction: true,
        csvFile: null,
    };

    openModal = () => this.setState({ showModal: true, error: null, result: null });
    closeModal = () => this.setState({ showModal: false, loading: false });

    onCsvChange = (e) => {
        this.setState({ csvFile: e.target.files[0] || null });
    };

    onReconChange = (e) => {
        this.setState({ useReconstruction: e.target.checked });
    };

    onGenerate = async () => {
        const { csvFile, useReconstruction } = this.state;
        const { task, apiURL } = this.props;

        if (!csvFile) {
            this.setState({ error: "Please select an Emlid CSV file." });
            return;
        }

        this.setState({ loading: true, error: null, result: null });

        const formData = new FormData();
        formData.append("emlid_csv", csvFile);
        formData.append("use_reconstruction", useReconstruction ? "true" : "false");

        try {
            const resp = await fetch(
                `${apiURL}/task/${task.id}/generate`,
                {
                    method: "POST",
                    body: formData,
                    headers: {
                        "X-CSRFToken": this.getCookie("csrftoken"),
                    },
                    credentials: "same-origin",
                }
            );
            const data = await resp.json();

            if (!resp.ok) {
                this.setState({ error: data.error || "Server error", loading: false });
            } else {
                this.setState({ result: data, loading: false });
            }
        } catch (e) {
            this.setState({ error: e.message, loading: false });
        }
    };

    getCookie(name) {
        const v = document.cookie.match("(^|;) ?" + name + "=([^;]*)(;|$)");
        return v ? v[2] : null;
    }

    render() {
        const { showModal, loading, error, result, useReconstruction } = this.state;

        return (
            <div>
                <button
                    className="btn btn-sm btn-secondary"
                    onClick={this.openModal}
                    title="Generate GCP pixel estimates from Emlid CSV"
                >
                    <i className="fa fa-crosshairs" /> Generate GCP Estimates
                </button>

                {showModal && (
                    <div
                        className="modal"
                        style={{ display: "block", background: "rgba(0,0,0,0.5)" }}
                    >
                        <div className="modal-dialog">
                            <div className="modal-content">
                                <div className="modal-header">
                                    <h5 className="modal-title">Generate GCP Estimates</h5>
                                    <button
                                        type="button"
                                        className="close"
                                        onClick={this.closeModal}
                                    >
                                        <span>&times;</span>
                                    </button>
                                </div>
                                <div className="modal-body">
                                    <div className="form-group">
                                        <label>Emlid CSV (required)</label>
                                        <input
                                            type="file"
                                            className="form-control-file"
                                            accept=".csv"
                                            onChange={this.onCsvChange}
                                        />
                                        <small className="form-text text-muted">
                                            Export from Emlid Flow app. Only FIX-quality points are used.
                                        </small>
                                    </div>

                                    <div className="form-check mt-2">
                                        <input
                                            type="checkbox"
                                            className="form-check-input"
                                            id="use-recon"
                                            checked={useReconstruction}
                                            onChange={this.onReconChange}
                                        />
                                        <label className="form-check-label" htmlFor="use-recon">
                                            Use reconstruction.json if available (more accurate)
                                        </label>
                                    </div>

                                    {error && (
                                        <div className="alert alert-danger mt-3">{error}</div>
                                    )}

                                    {result && (
                                        <div className="alert alert-success mt-3">
                                            <p>GCP estimates generated successfully.</p>
                                            <a
                                                href={result.gcpeditpro_txt}
                                                className="btn btn-sm btn-primary mr-2"
                                                download
                                            >
                                                Download gcpeditpro.txt
                                            </a>
                                            <a
                                                href={result.estimates_json}
                                                className="btn btn-sm btn-secondary"
                                                download
                                            >
                                                Download estimates.json
                                            </a>
                                        </div>
                                    )}
                                </div>
                                <div className="modal-footer">
                                    <button
                                        className="btn btn-secondary"
                                        onClick={this.closeModal}
                                        disabled={loading}
                                    >
                                        Close
                                    </button>
                                    <button
                                        className="btn btn-primary"
                                        onClick={this.onGenerate}
                                        disabled={loading}
                                    >
                                        {loading ? (
                                            <>
                                                <span
                                                    className="spinner-border spinner-border-sm mr-1"
                                                    role="status"
                                                />
                                                Running…
                                            </>
                                        ) : (
                                            "Generate"
                                        )}
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        );
    }
}
