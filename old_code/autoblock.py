import subprocess

def apply_sdn_rule(action, target_ip, switch="s1"):
    if action == "BLOCK":
        print(f"\n🛑 [CONTROLLER ALARM] Threat detected from {target_ip}!")
        print(f"⚙️  Pushing OpenFlow DROP rule to Switch '{switch}'...")
        # REMOVED 'sudo' from here
        command = f"ovs-ofctl -O OpenFlow13 add-flow {switch} priority=50000,ip,nw_src={target_ip},actions=drop"
        
    elif action == "ALLOW":
        print(f"\n✅ [CONTROLLER UPDATE] Clearing threat for {target_ip}...")
        print(f"⚙️  Removing OpenFlow rule from Switch '{switch}'...")
        # REMOVED 'sudo' from here
        command = f"ovs-ofctl -O OpenFlow13 del-flows {switch} ip,nw_src={target_ip}"
    
    else:
        return

    try:
        subprocess.run(command, shell=True, check=True)
        print("✔️  Switch Flow Table updated successfully.\n")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error communicating with switch: {e}")

if __name__ == "__main__":
    attacker = "10.0.0.1"
    apply_sdn_rule("BLOCK", attacker)
    
    import time
    print("Waiting 5 seconds before restoring traffic...")
    time.sleep(5)
    
    apply_sdn_rule("ALLOW", attacker)
    