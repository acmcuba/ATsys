from typing import Dict, List

from .event_catalog import EventFactory


def profile_power_fault_chain(factory: EventFactory, sequence_id: str) -> List[dict]:
    return [
        factory.build_event(
            sequence_id=sequence_id,
            event_code="ILOM-PWR",
            event_class="Fault",
            subclass="Power",
            severity="Critical",
            component="Power_Distribution",
            location="PDB / J58-J123 / JSB2 loop",
            fru="PDB_Board",
            sensor="Power_Rail_Monitor",
            test_phase="INIT",
            description="Power Fault detected in the server power distribution loop.",
            details={
                "expected_state": "Stable power rails",
                "observed_state": "Fault detected",
                "correlation_hint": "Check J58, J123, JSB2, C_Link, HMC-SP path",
                "recommended_playbook": "PLAYBOOK_POWER_FAULT"
            },
            tags=["power", "fault", "pdb", "critical"]
        ),
        factory.build_event(
            sequence_id=sequence_id,
            event_code="ILOM-HMC",
            event_class="Fault",
            subclass="Hardware",
            severity="Major",
            component="HMC",
            location="SP board / HMC link",
            fru="HMC_Module",
            sensor="HMC_Presence",
            test_phase="INIT",
            description="HMC not responding after power fault condition.",
            details={
                "expected_state": "Responding",
                "observed_state": "No response",
                "correlation_hint": "Possible downstream effect of power instability",
                "recommended_playbook": "PLAYBOOK_HMC_SP_LINK"
            },
            tags=["hmc", "power_chain", "major"]
        ),
        factory.build_event(
            sequence_id=sequence_id,
            event_code="ILOM-I2C",
            event_class="Fault",
            subclass="Communication",
            severity="Major",
            component="Management_Bus",
            location="SP sideband bus",
            fru="SP_Board",
            sensor="I2C_Bus_Status",
            test_phase="SYSTEM",
            description="I2C communication failure detected after power fault.",
            details={
                "expected_state": "Bus healthy",
                "observed_state": "Communication failure",
                "correlation_hint": "Validate HMC, sideband headers, power loop integrity",
                "recommended_playbook": "PLAYBOOK_I2C_GENERAL"
            },
            tags=["i2c", "sideband", "power_chain"]
        ),
    ]


def profile_mb2_bent_pin_chain(factory: EventFactory, sequence_id: str) -> List[dict]:
    return [
        factory.build_event(
            sequence_id=sequence_id,
            event_code="ILOM-MB2",
            event_class="Fault",
            subclass="Communication",
            severity="Critical",
            component="OSFP_MB2",
            location="Right Bianca / Right Mezz / MB2",
            fru="MB2_Cable_Right",
            sensor="MB2_I2C_Link",
            test_phase="INIT",
            description="I2C communication failure detected on MB2 sideband.",
            details={
                "expected_state": "Link healthy",
                "observed_state": "No sideband communication",
                "correlation_hint": "Possible bent pin or damaged socket",
                "recommended_playbook": "PLAYBOOK_MB2_I2C_FAIL"
            },
            tags=["mb2", "i2c", "critical", "right_bianca"]
        ),
        factory.build_event(
            sequence_id=sequence_id,
            event_code="ILOM-OSFP",
            event_class="Fault",
            subclass="Link",
            severity="Major",
            component="OSFP_Right",
            location="Right Bianca / OSFP ports 2-3",
            fru="OSFP_Board",
            sensor="OSFP_Link_Status",
            test_phase="SYSTEM",
            description="Right OSFP link down after MB2 communication failure.",
            details={
                "expected_state": "Link up",
                "observed_state": "Link down",
                "correlation_hint": "Follow MB2 socket and cable inspection",
                "recommended_playbook": "PLAYBOOK_OSFP_LINK_DOWN"
            },
            tags=["osfp", "mb2", "link_down", "system"]
        ),
    ]


def profile_osfp_left_disconnected(factory: EventFactory, sequence_id: str) -> List[dict]:
    return [
        factory.build_event(
            sequence_id=sequence_id,
            event_code="ILOM-OSFP-L",
            event_class="Fault",
            subclass="Presence",
            severity="Major",
            component="OSFP_Left",
            location="Left Bianca / OSFP0_1 / MB1",
            fru="OSFP_Board_Left",
            sensor="OSFP_Presence_Left",
            test_phase="INIT",
            description="Left OSFP cable disconnected or not fully seated.",
            details={
                "expected_state": "Cable present and latched",
                "observed_state": "Disconnected / not seated",
                "correlation_hint": "Check MB1 latch, seating, and cable alignment",
                "recommended_playbook": "PLAYBOOK_MB1_DISCONNECT"
            },
            tags=["osfp", "left", "mb1", "presence"]
        )
    ]


def profile_cx7_host_nic_down(factory: EventFactory, sequence_id: str) -> List[dict]:
    return [
        factory.build_event(
            sequence_id=sequence_id,
            event_code="ILOM-CX7",
            event_class="Fault",
            subclass="Connectivity",
            severity="Critical",
            component="CX7_NIC",
            location="Riser / MCIO / NIC slot",
            fru="CX7_Card",
            sensor="NIC_Link_Status",
            test_phase="SYSTEM",
            description="HOST NIC Down detected on CX7 adapter.",
            details={
                "expected_state": "NIC operational",
                "observed_state": "Link down",
                "correlation_hint": "Check riser cable seating, MCIO routing, riser gap",
                "recommended_playbook": "PLAYBOOK_CX7_HOST_NIC_DOWN"
            },
            tags=["cx7", "host_nic_down", "critical", "riser"]
        )
    ]


def profile_bp_i2c_fail_ssd_not_present(factory: EventFactory, sequence_id: str) -> List[dict]:
    return [
        factory.build_event(
            sequence_id=sequence_id,
            event_code="ILOM-BP",
            event_class="Fault",
            subclass="Communication",
            severity="Major",
            component="Backplane",
            location="BP / MCIO path",
            fru="Backplane_Module",
            sensor="BP_I2C_Status",
            test_phase="INIT",
            description="I2C fail for backplane detected.",
            details={
                "expected_state": "Healthy BP communication",
                "observed_state": "I2C fail",
                "correlation_hint": "Check BP cable, CX8/CX7 MCIO seating, connector J2/J7 where applicable",
                "recommended_playbook": "PLAYBOOK_BP_I2C_FAIL"
            },
            tags=["bp", "i2c", "init"]
        ),
        factory.build_event(
            sequence_id=sequence_id,
            event_code="ILOM-SSD",
            event_class="Fault",
            subclass="Presence",
            severity="Major",
            component="SSD_Backplane",
            location="Backplane / storage path",
            fru="SSD_Backplane",
            sensor="SSD_Presence",
            test_phase="SYSTEM",
            description="SSD not present reported after BP communication issue.",
            details={
                "expected_state": "SSD detected",
                "observed_state": "Not present",
                "correlation_hint": "Likely BP seating/cabling issue before replacing SSD",
                "recommended_playbook": "PLAYBOOK_SSD_NOT_PRESENT_BP_FIRST"
            },
            tags=["ssd", "bp", "system"]
        )
    ]


def profile_hmc_not_responding(factory: EventFactory, sequence_id: str) -> List[dict]:
    return [
        factory.build_event(
            sequence_id=sequence_id,
            event_code="ILOM-HMC",
            event_class="Fault",
            subclass="Hardware",
            severity="Critical",
            component="HMC",
            location="SP board / HMC header",
            fru="HMC_Module",
            sensor="HMC_Presence",
            test_phase="INIT",
            description="HMC not responding over management interface.",
            details={
                "expected_state": "Present and responding",
                "observed_state": "No response",
                "correlation_hint": "Check HMC cable, SP board header, physical pin condition",
                "recommended_playbook": "PLAYBOOK_HMC_SP_LINK"
            },
            tags=["hmc", "critical", "init"]
        )
    ]


PROFILE_REGISTRY: Dict[str, callable] = {
    "power_fault_chain": profile_power_fault_chain,
    "mb2_bent_pin_chain": profile_mb2_bent_pin_chain,
    "osfp_left_disconnected": profile_osfp_left_disconnected,
    "cx7_host_nic_down": profile_cx7_host_nic_down,
    "bp_i2c_fail_ssd_not_present": profile_bp_i2c_fail_ssd_not_present,
    "hmc_not_responding": profile_hmc_not_responding,
}
