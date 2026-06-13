from domain.models.enums.report_status import ReportStatus, ALLOWED_STATUS_TRANSITIONS


def test_new_can_go_to_in_progress():
    assert ReportStatus.IN_PROGRESS in ALLOWED_STATUS_TRANSITIONS[ReportStatus.NEW]


def test_new_can_go_to_rejected():
    assert ReportStatus.REJECTED in ALLOWED_STATUS_TRANSITIONS[ReportStatus.NEW]


def test_new_cannot_go_to_resolved():
    assert ReportStatus.RESOLVED not in ALLOWED_STATUS_TRANSITIONS[ReportStatus.NEW]


def test_new_cannot_stay_new():
    assert ReportStatus.NEW not in ALLOWED_STATUS_TRANSITIONS[ReportStatus.NEW]


def test_in_progress_can_go_to_resolved():
    assert ReportStatus.RESOLVED in ALLOWED_STATUS_TRANSITIONS[ReportStatus.IN_PROGRESS]


def test_in_progress_can_go_to_rejected():
    assert ReportStatus.REJECTED in ALLOWED_STATUS_TRANSITIONS[ReportStatus.IN_PROGRESS]


def test_in_progress_cannot_go_to_new():
    assert ReportStatus.NEW not in ALLOWED_STATUS_TRANSITIONS[ReportStatus.IN_PROGRESS]


def test_resolved_has_no_transitions():
    assert ALLOWED_STATUS_TRANSITIONS[ReportStatus.RESOLVED] == []


def test_rejected_has_no_transitions():
    assert ALLOWED_STATUS_TRANSITIONS[ReportStatus.REJECTED] == []


def test_all_statuses_are_in_fsm():
    for status in ReportStatus:
        assert status in ALLOWED_STATUS_TRANSITIONS


def test_new_has_exactly_two_allowed_transitions():
    assert len(ALLOWED_STATUS_TRANSITIONS[ReportStatus.NEW]) == 2


def test_in_progress_has_exactly_two_allowed_transitions():
    assert len(ALLOWED_STATUS_TRANSITIONS[ReportStatus.IN_PROGRESS]) == 2
