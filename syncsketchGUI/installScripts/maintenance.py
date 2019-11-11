import pkg_resources
import syncsketchGUI
import os
import urllib2
import sys

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
from syncsketchGUI.installScripts import installGui
from syncsketchGUI.lib import user as user

def getLatestSetupPyFileFromRepo():
    """Parses latest setup.py's version number"""
    response = urllib2.urlopen(
        'https://raw.githubusercontent.com/syncsketch/syncsketch-maya/release/setup.py')
    html = response.read()
    return html.split("version = '")[1].split("',")[0]


def getLatestSetupPyFileFromLocal():
    """Checks locally installed packages version number"""
    import pkg_resources
    #reload module to make sure we have loaded the latest live install
    reload(pkg_resources)
    local = pkg_resources.get_distribution(
        "syncSketchGUI").version
    return local


def getVersionDifference():
    """Returns the difference between local Package and latest Remote"""
    remote = int(getLatestSetupPyFileFromRepo().replace(".", ""))
    local = int(getLatestSetupPyFileFromLocal().replace(".", ""))
    if remote > local:
        return remote-local
    else:
         pass

def overwriteLatestInstallerFile():
    import urllib2
    """Parses latest setup.py's version number"""
    response = urllib2.urlopen(
        'https://raw.githubusercontent.com/syncsketch/syncsketch-maya/release/syncsketchGUI/installScripts/installGui.py')
    data = response.read()

    #Let's get the path of the installer
    installerPath = installGui.__file__[:-1]


    #Replace the module
    with open(installerPath, "w") as file:
        file.write(data)


def handleUpgrade():
    # * Check for Updates and load Upgrade UI if Needed
    if getVersionDifference():
        logger.info("YOU ARE {} VERSIONS BEHIND".format(getVersionDifference()))
        if os.getenv("SS_DISABLE_UPGRADE"):
            logging.info("The environment-Value SS_DISABLE_UPGRADE is set, skipping upgrade")
            return
        #Let's first make sure to replace the installerGui with the latest.
        # * we might restore old file if not continued from here
        overwriteLatestInstallerFile()

        #Make sure we only show this window once per Session
        if not installGui.InstallOptions.upgrade == 1:
            reload(installGui)
            #If this is set to 1, it means upgrade was already installed
            installGui.InstallOptions.upgrade = 1

            #Preserve Credentials
            current_user = user.SyncSketchUser()

            if current_user.is_logged_in():
                installGui.InstallOptions.tokenData['username'] = current_user.get_name()
                installGui.InstallOptions.tokenData['token'] = current_user.get_token()
                installGui.InstallOptions.tokenData['api_key'] = current_user.get_api_key()
                print("This is: {}".format(installGui.InstallOptions.tokenData))
            Installer = installGui.SyncSketchInstaller()
            Installer.showit()

    else:
        logger.info("You are using the latest release of this package")