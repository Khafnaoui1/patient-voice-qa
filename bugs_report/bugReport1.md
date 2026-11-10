### Bug 001 — Inconsistent handling of appointment request after patient lookup failure

**Severity:** Medium (potential usability issue)  
**Test:** Scenario 1 — Routine Appointment Scheduling  
**Evidence:** `patient-test-scenario 1.txt`, lines 31–35

**Expected behavior:**  
If the receptionist cannot locate a patient record, it should clearly explain whether it can continue with appointment booking or must transfer the caller to patient support.

**Actual behavior:**  
The receptionist stated that it could not find the patient's record but offered to help with booking and other services. When the patient accepted the offer and repeated the scheduling request, the receptionist initiated a transfer instead.

**Impact:**  
The interaction creates confusion about which services remain available after a failed patient lookup. The patient receives no appointment and no clear explanation of why the offer to continue booking was withdrawn.

**Status:** Potential bug — requires validation against expected product behavior.