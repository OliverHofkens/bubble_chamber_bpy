import subprocess

from bubble_chamber_bpy import __version__

EXECUTABLE_NAME = "bubble-chamber-bpy"


def test_some_help_can_be_printed_for_the_application():
    proc = subprocess.run([EXECUTABLE_NAME, "--help"])

    assert proc.returncode == 0


def test_the_version_of_the_application_can_be_printed():
    proc = subprocess.run([EXECUTABLE_NAME, "--version"], stdout=subprocess.PIPE)

    assert proc.returncode == 0
    assert __version__ in proc.stdout.decode("utf-8")
