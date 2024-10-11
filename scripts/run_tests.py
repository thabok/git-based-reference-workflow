import os
import sys
from datetime import datetime

from btc_embedded import EPRestApi, util

work_dir = os.path.abspath(os.path.dirname(os.path.dirname(sys.argv[0])))
epp_file = os.path.join(work_dir, 'model', 'avg_speed.epx')
project_name = os.path.basename(epp_file)[:-4]
report_dir = os.path.abspath('reports')

# BTC EmbeddedPlatform API object
ep = EPRestApi(install_location='E:/Product/ep.exe', version='24.3p0') # adapted to use latest ep build
# Load a BTC EmbeddedPlatform profile (*.epx)
ep.get(f"profiles/{epp_file}", message="Loading test project")
ep.put('architectures?performUpdateCheck=true', message="Parsing model and updating test project")

# Execute requirements-based tests
scopes = ep.get('scopes')
scope_uids = [scope['uid'] for scope in scopes]
toplevel_scope_uid = scope_uids[0]
rbt_exec_payload = {
    'UIDs': scope_uids,
    'data' : {
        'execConfigNames' : [ 'SL MIL (Toplevel)' ] # SL MIL / TL MIL / SIL
    }
}
exec_start_time = datetime.now()
response = ep.post('scopes/test-execution-rbt', rbt_exec_payload, message="Running requirements-based tests")
test_cases = ep.get('test-cases-rbt')

# Dump JUnit XML report
util.dump_testresults_junitxml(
    rbt_results=response,
    scopes=scopes,
    test_cases=test_cases,
    start_time=exec_start_time,
    project_name=project_name,
    output_file=os.path.join(work_dir, 'test_results.xml')
)

# Report test results to Polarion
polarion_cfg =  {
    'settings': [
        { 'key': 'Host', 'value': 'http://polarion03.prom.local' },
        { 'key': 'Port', 'value': '80' },
        { 'key': 'Work Item Types', 'value': 'Test Case' },
        { 'key': 'Linked Requirement Role', 'value': 'verifies' },
        { 'key': 'Project ID', 'value': 'http://polarion03.prom.local/polarion/redirect/project/avgspeed' },
        { 'key': 'username', 'value': os.environ['POLARION_USERNAME'] },
        { 'key': 'pwd', 'value': os.environ['POLARION_PWD'] }
    ],
    'execConfigNames': ['SL MIL (Toplevel)'],
    'requirementsSourceUid' : ep.get('requirements-sources')[0]['uid'],
    'syncMode': 'EP',
    'testStepsConsidered': True
}
ep.post('test-case-source-sync', polarion_cfg, message="Reporting test results to Polarion")

# Create project report
report = ep.post(f"scopes/{toplevel_scope_uid}/project-report", message="Creating test report")
# export project report to a file called 'report.html'
ep.post(f"reports/{report['uid']}", { 'exportPath': report_dir, 'newName': 'report' })

# Save *.epp
ep.put('profiles', { 'path': epp_file }, message="Saving test project")

print(f'Finished')
