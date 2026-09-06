from . import __version__ as app_version

app_name = "work_management"
app_title = "Work Management"
app_publisher = "VEQTA"
app_description = "Unified operational work management for Frappe Framework"
app_license = "MIT"

fixtures = [
    {
        "dt": "Role",
        "filters": [["role_name", "in", ["Work User", "Work Manager"]]],
    }
]
