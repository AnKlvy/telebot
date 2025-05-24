from student.handlers.test_report import TestReportStates, show_test_report_menu, choose_course_entry_subject, show_course_entry_test_result, choose_month_entry_subject, choose_month_entry_month, show_month_entry_test_result, choose_month_control_subject, choose_month_control_month, show_month_control_test_result

# Словарь переходов между состояниями
STATE_TRANSITIONS = {
    TestReportStates.course_entry_subject: TestReportStates.main,
    TestReportStates.test_result: TestReportStates.main,
    TestReportStates.month_entry_subject: TestReportStates.main,
    TestReportStates.month_entry_month: TestReportStates.month_entry_subject,
    TestReportStates.month_control_subject: TestReportStates.main,
    TestReportStates.month_control_month: TestReportStates.month_control_subject,
    TestReportStates.main: None  # None означает возврат в главное меню
}

# Словарь обработчиков для каждого состояния
STATE_HANDLERS = {
    TestReportStates.main: show_test_report_menu,
    TestReportStates.course_entry_subject: choose_course_entry_subject,
    TestReportStates.test_result: show_test_report_menu,
    TestReportStates.month_entry_subject: choose_month_entry_subject,
    TestReportStates.month_entry_month: choose_month_entry_month,
    TestReportStates.month_control_subject: choose_month_control_subject,
    TestReportStates.month_control_month: choose_month_control_month
}