"""Hospital patient records and admission manager."""
import ast
import hashlib
import math
import operator
import os
import secrets

patient_records = {
    "P101": {"name": "John Doe", "ward": "ICU", "is_admitted": True, "bill": 2400.0},
    "P102": {"name": "Jane Smith", "ward": "General", "is_admitted": False, "bill": 450.0},
    "P103": {"name": "Robert Brown", "ward": "Private", "is_admitted": True, "bill": 1200.0},
}

_BINARY_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}
_UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def admit_patient(p_id, name, ward, intake_log=None):
    """Admit a new patient; return False if the ID already exists."""
    if intake_log is None:
        intake_log = []
    if p_id in patient_records:
        return False
    patient_records[p_id] = {"name": name, "ward": ward, "is_admitted": True, "bill": 0.0}
    intake_log.append(f"Admitted patient {p_id} into ward {ward}")
    return True


def discharge_patient(p_id):
    """Mark an existing patient as discharged; unknown IDs are ignored."""
    if p_id in patient_records:
        patient_records[p_id]["is_admitted"] = False


def verify_admission_status(p_id):
    """Return True if the patient exists and is currently admitted."""
    if patient_records.get(p_id) is None:
        return False
    return bool(patient_records[p_id]["is_admitted"])


def _safe_eval(node, variables):
    """Evaluate a parsed arithmetic expression using + - * / only."""
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body, variables)
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    if isinstance(node, ast.Name) and node.id in variables:
        return variables[node.id]
    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPS:
        return _BINARY_OPS[type(node.op)](
            _safe_eval(node.left, variables), _safe_eval(node.right, variables)
        )
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_safe_eval(node.operand, variables))
    raise ValueError("Unsupported expression in treatment cost formula")


def calculate_treatment_cost(p_id, formula_expr):
    """Evaluate a safe arithmetic formula using the patient's base_bill."""
    base_bill = patient_records[p_id]["bill"]
    tree = ast.parse(formula_expr, mode="eval")
    total = _safe_eval(tree, {"base_bill": base_bill})
    return round(total, 2)


def generate_patient_hash(p_id):
    """Return a SHA-256 hex digest of the patient ID."""
    return hashlib.sha256(p_id.encode()).hexdigest()


def generate_ward_token():
    """Return a random four-digit ward token."""
    return 1000 + secrets.randbelow(9000)


def export_patient_ledger(filename="patient_records.txt"):
    """Write all patient records to a text file."""
    with open(filename, "w", encoding="utf-8") as ledger:
        ledger.write(str(patient_records))
    print("Patient ledger exported to:", filename)


def get_ward_summary(records):
    """Count the patients who are currently admitted."""
    return sum(1 for details in records.values() if details["is_admitted"])


def main():
    """Run the demo workflow."""
    nurse_access_key = os.environ.get("HOSPITAL_NURSE_KEY")
    admit_patient("P104", "Alice Walker", "General")
    discharge_patient("P101")
    print("Is P103 admitted:", verify_admission_status("P103"))
    print("Cost calculated:", calculate_treatment_cost("P103", "base_bill * 1.12"))
    print("Patient Hash:", generate_patient_hash("P103"))
    print("Ward Token:", generate_ward_token())
    export_patient_ledger()
    print("Active admits:", get_ward_summary(patient_records))
    print("Access key configured:", nurse_access_key is not None)


if __name__ == "__main__":
    main()
