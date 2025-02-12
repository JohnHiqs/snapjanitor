import ssl
import atexit
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim

def get_snapshots_recursively(vm, snapshots):
    for snapshot in vm.snapshot.rootSnapshotList:
        snapshots.append((snapshot, vm))
        get_snapshots_recursively(snapshot, snapshots)

def remove_snapshots(snapshots_to_remove):
    for snapshot, vm in snapshots_to_remove:
        print(f"Removing snapshot '{snapshot.name}' from VM '{vm.name}' on host '{vm.runtime.host.name}'")
        task = snapshot.snapshot.RemoveSnapshot_Task(removeChildren=False)
        task.WaitForTask()

def main():
    # vCenter connection details
    vcenter_host = 'your_vcenter_host'
    vcenter_user = 'your_username'
    vcenter_password = 'your_password'

    # Disable SSL certificate verification
    context = ssl._create_unverified_context()

    # Connect to vCenter
    si = SmartConnect(host=vcenter_host, user=vcenter_user, pwd=vcenter_password, sslContext=context)
    atexit.register(Disconnect, si)

    # Get the content
    content = si.RetrieveContent()

    # Get all VMs
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    vms = container.view
    container.Destroy()

    # List to hold snapshots and their corresponding VMs
    snapshots = []

    # Iterate through all VMs and get snapshots
    for vm in vms:
        if vm.snapshot:
            get_snapshots_recursively(vm, snapshots)

    # Print the snapshots and corresponding VM names
    print(f"{'Snapshot Name':<30} {'VM Name':<30} {'Host Name':<30}")
    print("="*90)
    for snapshot, vm in snapshots:
        host_name = vm.runtime.host.name if vm.runtime.host else 'N/A'
        print(f"{snapshot.name:<30} {vm.name:<30} {host_name:<30}")

    # Read the list of hostnames from a file
    hostnames_file = 'hostnames.txt'
    with open(hostnames_file, 'r') as file:
        hostnames_to_search = [line.strip() for line in file.readlines()]

    # Find snapshots for the specified hostnames
    snapshots_to_remove = []
    for snapshot, vm in snapshots:
        if vm.runtime.host.name in hostnames_to_search:
            snapshots_to_remove.append((snapshot, vm))

    # Display the snapshots to be removed
    if snapshots_to_remove:
        print("\nSnapshots to be removed:")
        print(f"{'Snapshot Name':<30} {'VM Name':<30} {'Host Name':<30}")
        print("="*90)
        for snapshot, vm in snapshots_to_remove:
            host_name = vm.runtime.host.name if vm.runtime.host else 'N/A'
            print(f"{snapshot.name:<30} {vm.name:<30} {host_name:<30}")

        # Confirm removal
        confirm = input("\nType 'CONFIRM' to proceed with the removal of the above snapshots: ")
        if confirm == 'CONFIRM':
            remove_snapshots(snapshots_to_remove)
            print("Snapshots removed successfully.")
        else:
            print("Snapshot removal aborted.")
    else:
        print("No snapshots found for the specified hostnames.")

if __name__ == "__main__":
    main()
