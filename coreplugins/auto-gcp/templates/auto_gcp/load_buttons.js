PluginsAPI.Dashboard.addTaskActionButton(
    ["{{ app_name }}/build/TaskView.js"],
    function(args, TaskView) {
        return React.createElement(TaskView, {
            task: args.task,
            apiURL: "{{ api_url }}"
        });
    }
);
