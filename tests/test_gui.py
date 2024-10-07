import pytest
from GUI import *
# run export PYTHONPATH=$(pwd) in terminal

@pytest.fixture
def gui_app(mocker):
    mocker.patch('customtkinter.CTk.mainloop')
    app = mainGUI()

    audio_menu = audioMenu(app)

    audio_menu.uploadButton = mocker.Mock()
    audio_menu.recordButton = mocker.Mock() 

    app.audioMenuList = [audio_menu]

    yield app
    app.destroy()

def test_upload_button_calls_function(gui_app, mocker):
    mock_upload = mocker.patch.object(gui_app.audioMenuList[0], 'uploadAudio')

    gui_app.audioMenuList[0].uploadAudio()
    mock_upload.assert_called_once()

def test_record_button_calls_function(gui_app, mocker):
    mock_record = mocker.patch.object(gui_app.audioMenuList[0], 'recordAudio')
    gui_app.audioMenuList[0].recordAudio()
    mock_record.assert_called_once()