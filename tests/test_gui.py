import pytest
import time
import sys
from GUI import *

@pytest.fixture
def gui_app():
    # instantiate the main GUI app
    app = mainGUI()
    yield app
    app.destroy()

def invoke_upload_button_and_measure_time(gui_app, mocker):
    start_time = time.time()

    # mock the uploadAudio method to simulate user upload action
    mocker.path('GUI.audioMenu.uploadAudio')

    # invoke the upload button
    gui_app.audioMenuList[0].uploadButton.invoke()

    elapsed_time = time.time() - start_time
    return elapsed_time

def invoke_record_button_and_measure_time(gui_app, mocker):
    start_time = time.time()

    # mock recordAudio method to simulate user record action
    mocker.patch('GUI.audioMenu.recordAudio')

    # invoke record button
    gui_app.audioMenuList[0].recordButton.invoke()

    elapsed_time = time.time() - start_time
    return elapsed_time

@pytest.mark.skipif(sys.version_info >= (3, 11, 7), reason="Only run on Python versions before 3.11.7")
def test_upload_button_responsiveness_before_fix(gui_app, mocker):
    elapsed_time = invoke_upload_button_and_measure_time(gui_app, mocker)
    assert elapsed_time < 3, "Upload button response was too slow in Python 3.11.6 or lower"

@pytest.mark.skipif(sys.version_info < (3, 11, 7), reason="Only run on Python versions 3.11.7 or higher")
def test_upload_button_responsiveness_after_fix(gui_app, mocker):
    elapsed_time = invoke_upload_button_and_measure_time(gui_app, mocker)
    assert elapsed_time < 1, "Upload button response was slow in Python 3.11.7 or higher"

@pytest.mark.skipif(sys.version_info >= (3, 11, 7), reason="Only run on Python versions before 3.11.7")
def test_record_button_responsiveness_before_fix(gui_app, mocker):
    elapsed_time = invoke_record_button_and_measure_time(gui_app, mocker)
    assert elapsed_time < 3, "Record button response was too slow in Python 3.11.6 or lower"

@pytest.mark.skipif(sys.version_info < (3, 11, 7), reason="Only run on Python versions 3.11.7 or higher")
def test_record_button_responsiveness_after_fix(gui_app, mocker):
    elapsed_time = invoke_record_button_and_measure_time(gui_app, mocker)
    assert elapsed_time < 1, "Record button response was slow in Python 3.11.7 or higher"