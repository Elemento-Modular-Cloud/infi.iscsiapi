from infi.execute import execute_assert_success

def get_platform_specific_iscsi_service():
    from infi.os_info import get_platform_string
    platform = get_platform_string()
    if platform.startswith('windows'):
        return ISCSIWindowsServiceStates()
    elif platform.startswith('linux'):
        return ISCSILinuxServiceStates()
    elif platform.startswith('solaris'):
        return ISCSISolarisServiceStates()
    else:
        raise ImportError("not supported on this platform")

class ISCSIServiceStates(object):
    def start(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

class ISCSILinuxServiceStates(ISCSIServiceStates):
    def stop(self):
        execute_assert_success(['iscsiadm', '-m', 'node', '-u'])

    def start(self):
        execute_assert_success(['iscsiadm', '-m', 'node', '-l'])


class ISCSIWindowsServiceStates(ISCSIServiceStates):
    def stop(self):
        from infi.iscsiapi import get_iscsiapi
        api = get_iscsiapi()
        sessions = api.get_sessions()
        for session in sessions:
            api.logout(session)

    def start(self):
        process = execute_assert_success(['iscsicli', 'listtargets'])
        output = process.get_stdout().splitlines()
        for line in output:
            if "infinibox" in line:
                execute_assert_success(['iscsicli', 'QLoginTarget', line.strip()])

class ISCSISolarisServiceStates(ISCSIServiceStates):
    def start(self):
        from infi.iscsiapi import get_iscsiapi
        api = get_iscsiapi()
        api._enable_iscsi_auto_login()

    def stop(self):
        from infi.iscsiapi import get_iscsiapi
        api = get_iscsiapi()
        api._disable_iscsi_auto_login()
