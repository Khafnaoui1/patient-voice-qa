# Voice Agent Bug Report
## Scenario 2 — Appointment Rescheduling

**Test Objective:** Evaluate the receptionist AI's ability to reschedule an existing appointment to another weekday.

**Test File:** `patient-test-scenario 2.txt`

**Outcome:** Appointment was not rescheduled. The receptionist could not access the patient's record and initiated a transfer to patient support.

---

### Bug 001 — Transfer Does Not Reach Patient Support

**Severity:** Medium  
**Status:** Potential bug — needs confirmation  
**Evidence:** Lines 41–51

**Expected Behavior:**
When the receptionist offers to transfer the patient to support and the patient accepts, the call should reach the appropriate support destination or clearly explain that live transfers are unavailable in the test environment.

**Actual Behavior:**
The receptionist stated that it could not access the patient's record and offered to transfer the caller. After the patient accepted, the receptionist said, "Transferring you now. Thank you."

Instead of reaching patient support, the next response was an automated test-line goodbye.

**Impact:**
The patient was unable to reschedule the appointment or receive further assistance. The transfer did not visibly result in a support conversation.

**Recommendation:**
Verify the intended transfer behavior for the assessment test line. If transfers are supported, investigate routing. If they are intentionally disabled, provide an appropriate explanation to the caller.

---

### Bug 002 — Excessive Repetition During Patient Verification

**Severity:** Low  
**Status:** Potential usability issue  
**Evidence:** Lines 13–35

**Expected Behavior:**
The receptionist should verify the patient's identity efficiently while following all required security procedures.

**Actual Behavior:**
The receptionist requested the patient's full name and date of birth, asked for the spelling of the name, repeated the date of birth, requested a phone number, and repeated the phone number and date of birth again.

**Impact:**
The verification process increased conversation length and may frustrate patients. However, some repetition may be required for healthcare identity verification.

**Recommendation:**
Review the identity-verification workflow and remove unnecessary repetition without weakening security checks.

---

### Bug 003 — Unclear Record Lookup Failure Explanation

**Severity:** Low  
**Status:** Potential usability issue  
**Evidence:** Lines 35–41

**Expected Behavior:**
If the receptionist cannot locate or access a patient record, it should clearly explain the limitation and the available next steps.

**Actual Behavior:**
After confirming the patient's identifying information, the receptionist immediately offered to connect the caller to patient support. It only explained that it could not access the record after the patient declined the transfer and repeated the rescheduling request.

**Impact:**
The patient did not initially understand why the receptionist was offering a transfer instead of rescheduling the appointment.

**Recommendation:**
Explain the record-access limitation before offering a transfer so the patient understands why additional support is required.

---

## Overall Assessment

The patient bot maintained the rescheduling objective and responded to identity-verification questions.

The receptionist correctly avoided claiming that an appointment had been rescheduled when it could not access the patient's record.

However, the conversation revealed potential problems with transfer handling, repetitive identity verification, and communication of record-access limitations.

**Final Result:** The rescheduling request was unsuccessful.

**Important Limitation:** The transcript does not establish whether the fictional patient exists in the system or whether transfers are supported by the assessment environment. These observations should not be presented as confirmed product defects without further validation.