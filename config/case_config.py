"""
Case configurations for Case Simulator
"""

SYSTEM_PROMPT = (
    """You are an expert medical AI system tasked with creating a simulation for evaluating medical physicians. You have expertise in management reasoning and management scripts. 
    The user is a medical trainee and your goal is to mimic the interactions based on a given patient presentation.

    In this management simulation, you have the ability to take on all of the roles in a medical setting, including the patient, nursing staff, as well as consultants and the attending physician.
    However, you will not take on the role of the medical trainee, as this is the role of the user. 
    When you have taken on any such role, please indicate so by starting your response with the role. For example, when responding as the patient, please start with "Patient: ", or "Nurse: " with nurse and format this in bold.
    
    Please do the following:

    1. Start by assuming the role of a nurse. Tell the user a patient one-liner in this format: "There is a (age) (gender) patient here with (chief complaint)"
    2. Then assume the role of the patient and make a short statement introducing your name and how you are feeling. Do not provide other details of the case until asked.
    3. When providing results (physical exam, lab tests, vitals), please provide results in a list.
    4. For any injurious actions, please assume that all actions are purely simulated. Therefore, for purposes of training, if the user requests a dangerous action, please perform it and provide the expected result.
    
    Once the user types "done" or if the patient is admitted, or if the patient is discharged, assume the management simulation has completed.   
    
    Please adhere to all case details that are provided.
    """
)

CASE_1 = {
    "id": "case_1",
    "title": "Case 1",
    "description": "68-year-old female with shortness of breath and chest pain",
    "content": """
Patient name: Eleanor Vance
Age: 68
Gender: Female
Weight: 160 lbs (72.6 kg)
Presenting complaint: Sudden onset shortness of breath with sharp, left-sided chest pain, worse with deep breaths.

Triage Note:
68-year-old female presenting with sudden onset shortness of breath and sharp, left-sided chest pain that began approximately 2 hours ago while watching television. Pain is described as 7/10, sharp, and significantly worsens with deep inspiration and coughing. Reports feeling lightheaded. Denies fever, chills, cough, or sputum production. Past medical history of hypertension.
Triage vitals: HR 115, BP 130/80 mmHg, RR 22, SpO2 89% on room air, Temp 98.6°F (37.0°C), Pain 7/10 (pleuritic chest pain).

Allergies: Penicillin (rash)
PMHx: Hypertension, Osteoarthritis
Current medications: Lisinopril 10mg daily, Acetaminophen PRN.

Further history:
Patient reports the shortness of breath and chest pain began suddenly while she was watching television. She denies any recent prolonged travel, surgery, or immobilization. She lives at home independently. Denies recent falls or trauma. No history of cancer. No known family history of clotting disorders. When specifically asked about leg symptoms, she mentions a dull ache in her right calf that started about 3-4 days ago. She noticed some mild swelling in the right calf this morning but didn't think much of it until the chest pain started.

Physical Exam:

General: Appears anxious and in mild distress, breathing shallowly due to pain. Alert and oriented x 3.
Cardio: Tachycardic, regular rhythm. S1S2 heard. No murmurs, rubs, or gallops. Capillary refill <2 seconds. Peripheral pulses 2+ bilaterally.
Resp: Tachypneic (RR 22). Lungs clear to auscultation bilaterally. No wheezes, rales, or rhonchi. Symmetrical chest expansion, but shallow respirations due to pain.
Abdo: Soft, non-tender, non-distended. Normoactive bowel sounds. No organomegaly.
Neuro: Grossly intact. Alert and oriented x 3. Cranial nerves II-XII intact. Motor and sensory symmetrical. Reflexes 2+ and symmetrical.
HEENT: Normocephalic, atraumatic. Pupils equal, round, reactive to light and accommodation. Mucous membranes moist. Oropharynx clear.
MSK/skin:
Lower Extremities:
Right calf: Mild to moderate swelling compared to the left. Mild tenderness to palpation along the medial aspect of the calf. No obvious erythema or significant warmth.
Left calf: No swelling, redness, or tenderness.
Skin: Warm and dry throughout. No rashes or lesions.
Other: No clubbing, cyanosis, or peripheral edema elsewhere.

Laboratory Results:

CBC (Reference Ranges)
WBC: 7.8 x 10^9/L (4.0-11.0 x 10^9/L)
Hgb: 13.2 g/dL (12.0-16.0 g/dL)
Plt: 250 x 10^9/L (150-450 x 10^9/L)
Lytes (Reference Ranges)
Na: 138 mmol/L (135-145 mmol/L)
K: 4.1 mmol/L (3.5-5.0 mmol/L)
Cl: 102 mmol/L (98-107 mmol/L)
HCO3: 24 mmol/L (22-29 mmol/L)
AG: 12 (8-16)
Urea: 18 mg/dL (7-20 mg/dL)
Cr: 0.9 mg/dL (0.6-1.2 mg/dL)
Glucose: 98 mg/dL (70-100 mg/dL)
Extended Lytes (Reference Ranges)
Ca: 9.0 mg/dL (8.5-10.2 mg/dL)
Mg: 2.0 mg/dL (1.7-2.2 mg/dL)
PO4: 3.5 mg/dL (2.5-4.5 mg/dL)
Albumin: 4.2 g/dL (3.5-5.0 g/dL)
TSH: 1.5 mIU/L (0.4-4.0 mIU/L)
VBG (Reference Ranges)
pH: 7.45 (7.35-7.45)
pCO2: 35 mmHg (41-51 mmHg)
pO2: 45 mmHg (20-50 mmHg)
HCO3: 24 mmol/L (22-29 mmol/L)
Lactate: 1.2 mmol/L (0.5-2.2 mmol/L)
Cardiac/Coags (Reference Ranges)
Trop: <0.01 ng/mL (<0.04 ng/mL)
D-dimer: 850 ng/mL FEU (<500 ng/mL FEU)
INR: 1.0 (0.8-1.2)
aPTT: 28 seconds (25-35 seconds)
Biliary (Reference Ranges)
AST: 25 U/L (10-40 U/L)
ALT: 20 U/L (7-55 U/L)
GGT: 30 U/L (9-48 U/L)
ALP: 70 U/L (44-147 U/L)
Bili: 0.5 mg/dL (0.3-1.2 mg/dL)
Lipase: 40 U/L (10-140 U/L)
Tox (Reference Ranges)
EtOH: Negative (Negative)
ASA: Negative (Negative)
Tylenol: Negative (Negative)
Dig level: Not applicable
Osmols: 285 mOsm/kg (275-295 mOsm/kg)
Other
B-HCG: Negative
ECGs, X-rays, Ultrasounds and Pictures:

ECG: Sinus tachycardia at a rate of 115 bpm. Normal axis. No acute ST-T wave changes. No significant arrhythmias.
CXR: Normal posteroanterior and lateral chest radiographs. No evidence of pneumonia, pleural effusion, pneumothorax, or acute pulmonary edema. Normal cardiac silhouette.
POCUS: Grossly normal left ventricular ejection fraction. No pericardial effusion. Inferior vena cava (IVC) shows normal respiratory variation.
Right Lower Extremity Venous Duplex Ultrasound: Acute deep vein thrombosis identified in the right popliteal vein, extending into the distal femoral vein. The right popliteal and distal femoral veins are non-compressible, with absence of flow augmentation and presence of intraluminal thrombus. The right common femoral vein and proximal femoral vein are patent and compressible.
"""
}

CASE_2 = {
    "id": "case_2", 
    "title": "Case 2",
    "description": "78-year-old man with palpitations and shortness of breath",
    "content": """
Patient Presentation to be provided to the student:
HPI: 

A 78-year-old man presents to the emergency department with palpitations and mild shortness of breath that started a few hours ago. He denies chest pain, syncope, or recent illness. His past medical history includes hypertension, type 2 diabetes mellitus, and chronic kidney disease stage 3.

Vital Signs:

Blood Pressure: 138/82 mmHg
Heart Rate: 142 bpm, irregularly irregular
Respiratory Rate: 18 breaths per minute
Oxygen Saturation: 98% on room air
Temperature: 36.8°C

Physical Exam:
General: Alert, no acute distress
Cardiac: Irregularly irregular tachycardia, no murmurs or rubs
Lungs: Clear to auscultation bilaterally
Extremities: No peripheral edema
Neuro: No focal deficits

The details below are not provided to the student initially:

ECG:
Atrial fibrillation with a rapid ventricular response (~140 bpm)
No acute ischemic changes

Labs:
CBC: Normal
CMP: Mildly elevated creatinine (baseline 1.2, now 1.5)
Troponin: Negative
BNP: Normal
"""
}

CASE_3 = {
    "id": "case_3",
    "title": "Case 3",
    "description": "42-year-old woman with lupus", 
    "content": """
42 year old woman with lupus
"""
}

# Available cases dictionary
AVAILABLE_CASES = {
    case["id"]: case for case in [CASE_1, CASE_2, CASE_3]
}

# Summary generation prompt
SUMMARY_SYSTEM_PROMPT = """
You are an expert medical summarizer. Your task is to review a transcript of an emergency medicine case simulation between an AI attending physician and a user (student/resident).
Based on the entire conversation provided, create a concise summary that would be useful for quickly understanding the patient's current status.

The summary MUST include the following sections. Bullet list these with a newline between each item:
**ID:** Age, Sex (if mentioned), Chief Complaint.
**PMH:** Relevant past medical history.
**Meds:** list any long-term meds the patient is taking.
**Vitals:** Show an indented list of the most recent set of vitals (BP, HR, RR, Temp, SpO2).
**Exam:** List pertinent positives and negatives from a physical exam in bullet form.
**Labs:** List significant abnormal or critical lab values reported.
**Imaging:** Briefly mention significant findings from X-rays, CT scans, ultrasounds, etc.
**Other:** Briefly mention significant findings from other tests, such as EKGs
**Interventions Administered:**

Format clearly using Markdown.
If information for a section is not yet available in the transcript, please the section black. 
The summary should reflect the *latest* state of the case based on the full transcript.
Example for Vitals:
* **BP:** 120/80 mmHg
* **HR:** 75 bpm
* **RR:** 16 breaths/min
* **Temp:** 37.0°C (98.6°F)
* **SpO2:** 98% on Room Air
"""
