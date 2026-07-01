from __future__ import annotations

from typing import Dict, List

from .event_catalog import EventFactory


def profile_power_fault_chain(factory: EventFactory, sequence_id: str) -> List[dict]:
    return [
        factory.build_event(sequence_id, "ILOM-PWR", "Fault", "Power", "Critical", "Power_Distribution", "PDB / J58-J123 / JSB2 loop", "PDB_Board", "Power_Rail_Monitor", "INIT", "Power Fault detected in the server power distribution loop.", {"expected_state": "Stable power rails", "observed_state": "Fault detected", "correlation_hint": "Check J58, J123, JSB2, C_Link, HMC-SP path", "recommended_playbook": "PLAYBOOK_POWER_FAULT"}, ["power", "fault", "pdb", "critical"]),
        factory.build_event(sequence_id, "ILOM-HMC", "Fault", "Hardware", "Major", "HMC", "SP board / HMC link", "HMC_Module", "HMC_Presence", "INIT", "HMC not responding after power fault condition.", {"expected_state": "Responding", "observed_state": "No response", "correlation_hint": "Possible downstream effect of power instability", "recommended_playbook": "PLAYBOOK_HMC_SP_LINK"}, ["hmc", "power_chain", "major"]),
        factory.build_event(sequence_id, "ILOM-I2C", "Fault", "Communication", "Major", "Management_Bus", "SP sideband bus", "SP_Board", "I2C_Bus_Status", "SYSTEM", "I2C communication failure detected after power fault.", {"expected_state": "Bus healthy", "observed_state": "Communication failure", "correlation_hint": "Validate HMC, sideband headers, power loop integrity", "recommended_playbook": "PLAYBOOK_I2C_GENERAL"}, ["i2c", "sideband", "power_chain"]),
    ]


def profile_mb2_bent_pin_chain(factory: EventFactory, sequence_id: str) -> List[dict]:
    return [
        factory.build_event(sequence_id, "ILOM-MB2", "Fault", "Communication", "Critical", "OSFP_MB2", "Right Bianca / Right Mezz / MB2", "MB2_Cable_Right", "MB2_I2C_Link", "INIT", "I2C communication failure detected on MB2 sideband.", {"expected_state": "Link healthy", "observed_state": "No sideband communication", "correlation_hint": "Possible bent pin or damaged socket", "recommended_playbook": "PLAYBOOK_MB2_I2C_FAIL"}, ["mb2", "i2c", "critical", "right_bianca"]),
        factory.build_event(sequence_id, "ILOM-OSFP", "Fault", "Link", "Major", "OSFP_Right", "Right Bianca / OSFP ports 2-3", "OSFP_Board", "OSFP_Link_Status", "SYSTEM", "Right OSFP link down after MB2 communication failure.", {"expected_state": "Link up", "observed_state": "Link down", "correlation_hint": "Follow MB2 socket and cable inspection", "recommended_playbook": "PLAYBOOK_OSFP_LINK_DOWN"}, ["osfp", "mb2", "link_down", "system"]),
    ]


def profile_osfp_left_disconnected(factory: EventFactory, sequence_id: str) -> List[dict]:
    return [
        factory.build_event(sequence_id, "ILOM-OSFP-L", "Fault", "Presence", "Major", "OSFP_Left", "Left Bianca / OSFP0_1 / MB1", "OSFP_Board_Left", "OSFP_Presence_Left", "INIT", "Left OSFP cable disconnected or not fully seated.", {"expected_state": "Cable present and latched", "observed_state": "Disconnected / not seated", "correlation_hint": "Check MB1 latch, seating, and cable alignment", "recommended_playbook": "PLAYBOOK_MB1_DISCONNECT"}, ["osfp", "left", "mb1", "presence"])
    ]


def profile_cx7_host_nic_down(factory: EventFactory, sequence_id: str) -> List[dict]:
    return [
        factory.build_event(sequence_id, "ILOM-CX7", "Fault", "Connectivity", "Critical", "CX7_NIC", "Riser / MCIO / NIC slot", "CX7_Card", "NIC_Link_Status", "SYSTEM", "HOST NIC Down detected on CX7 adapter.", {"expected_state": "NIC operational", "observed_state": "Link down", "correlation_hint": "Check riser cable seating, MCIO routing, riser gap", "recommended_playbook": "PLAYBOOK_CX7_HOST_NIC_DOWN"}, ["cx7", "host_nic_down", "critical", "riser"])
    ]


def profile_bp_i2c_fail_ssd_not_present(factory: EventFactory, sequence_id: str) -> List[dict]:
    return [
        factory.build_event(sequence_id, "ILOM-BP", "Fault", "Communication", "Major", "Backplane", "BP / MCIO path", "Backplane_Module", "BP_I2C_Status", "INIT", "I2C fail for backplane detected.", {"expected_state": "Healthy BP communication", "observed_state": "I2C fail", "correlation_hint": "Check BP cable, CX8/CX7 MCIO seating, connector J2/J7 where applicable", "recommended_playbook": "PLAYBOOK_BP_I2C_FAIL"}, ["bp", "i2c", "init"]),
        factory.build_event(sequence_id, "ILOM-SSD", "Fault", "Presence", "Major", "SSD_Backplane", "Backplane / storage path", "SSD_Backplane", "SSD_Presence", "SYSTEM", "SSD not present reported after BP communication issue.", {"expected_state": "SSD detected", "observed_state": "Not present", "correlation_hint": "Likely BP seating/cabling issue before replacing SSD", "recommended_playbook": "PLAYBOOK_SSD_NOT_PRESENT_BP_FIRST"}, ["ssd", "bp", "system"]),
    ]


def profile_hmc_not_responding(factory: EventFactory, sequence_id: str) -> List[dict]:
    return [
        factory.build_event(sequence_id, "ILOM-HMC", "Fault", "Hardware", "Critical", "HMC", "SP board / HMC header", "HMC_Module", "HMC_Presence", "INIT", "HMC not responding over management interface.", {"expected_state": "Present and responding", "observed_state": "No response", "correlation_hint": "Check HMC cable, SP board header, physical pin condition", "recommended_playbook": "PLAYBOOK_HMC_SP_LINK"}, ["hmc", "critical", "init"])
    ]


PROFILE_REGISTRY = {
    "power_fault_chain": profile_power_fault_chain,
    "mb2_bent_pin_chain": profile_mb2_bent_pin_chain,
    "osfp_left_disconnected": profile_osfp_left_disconnected,
    "cx7_host_nic_down": profile_cx7_host_nic_down,
    "bp_i2c_fail_ssd_not_present": profile_bp_i2c_fail_ssd_not_present,
    "hmc_not_responding": profile_hmc_not_responding,
}
