#!/usr/bin/python3
# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=too-many-branches
# pylint: disable=too-few-public-methods
# pylint: disable=missing-function-docstring
# pylint: disable=raise-missing-from
# pylint: disable=bare-except

import argparse
import logging
import os
import platform
import shutil
import sys

import jinja2


# - - logging - - #
class ANSIColors:
    RES = "\033[0;39m"

    LRED = "\033[0;31m"
    LGRN = "\033[0;32m"
    LBLU = "\033[0;34m"
    LMGN = "\033[0;35m"
    LCYN = "\033[0;36m"

    BBLK = "\033[1;30m"
    BBLU = "\033[1;34m"
    BWHI = "\033[1;37m"

    def __init__(self):
        pass


_c = ANSIColors()


class ShutdownHandler(logging.StreamHandler):
    def emit(self, record):
        if record.levelno >= logging.ERROR:
            sys.exit(1)


class OTGFormatter(logging.Formatter):
    _FMT_BEGIN = f"{_c.BBLK}[{_c.BWHI}%(name)s{_c.BBLK}]["
    _FMT_END = f"{_c.BBLK}]{_c.RES}"
    _FORMATS = {
        logging.NOTSET: _c.LCYN,
        logging.DEBUG: _c.BWHI,
        logging.INFO: _c.BBLU,
        logging.WARNING: _c.LGRN,
        logging.ERROR: _c.LRED,
        logging.CRITICAL: _c.LRED,
    }

    def format(self, record):
        finfmt = f"{self._FMT_BEGIN}{self._FORMATS.get(record.levelno)}"
        finfmt += f"%(levelname)-.1s{self._FMT_END} %(message)s"

        return logging.Formatter(fmt=finfmt, validate=True).format(record)


# - - meaty bits - - #
class TemplateOTG:
    _PLATFORM_BLACKLIST = {
        "Darwin": [
            "bin/chromium",
            "bin/fetch.py",
            "bin/setcake.py",
            "bin/setgov",
            "bin/suspendtodisk",
            "bin/ttygrab",
            "share/multiwg-handler",
        ]
    }

    def __init__(self):
        self.logger = None
        self.context = None

    def _ln(self, src, dst):
        isdir = os.path.isdir(dst)

        if os.path.exists(dst):
            self.logger.warning("symlink   %s: exists, removing", dst)
            os.remove(dst)

        self.logger.info("symlink   %s", dst)
        try:
            os.symlink(src, dst, target_is_directory=isdir)
        except:
            self.logger.exception("symlink   %s: creating symlink failed")

    def _set_root_logger(self):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        formatter = OTGFormatter()
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        logger.addHandler(ShutdownHandler())

    def _prompt(self):
        # fmt: off
        msg  = f'platform         : {self.context["platform"]}\n'
        msg += f'home directory   : {self.context["home"]}\n'
        msg += f'install prefix   : {self.context["prefix"]}\n'
        msg += f'setboxes specific: {self.context["is_setboxes"]}\n'
        # fmt: on

        for line in msg.split("\n"):
            self.logger.info(line)

    def _parse_args(self):
        parser = argparse.ArgumentParser(description="OTG templater")
        parser.add_argument(
            "--prefix",
            type=str,
            help="installation prefix",
            default="/opt/mss",
        )
        parser.add_argument(
            "--home",
            type=str,
            help="$HOME of the user",
            default="/home/mss",
        )
        parser.add_argument(
            "--setboxes",
            action="store_true",
            help="enable gottaeat/setboxes specific functionality",
            default=False,
        )

        args = parser.parse_args()

        self.context = {
            "prefix": args.prefix,
            "home": args.home,
            "is_setboxes": args.setboxes,
            "platform": platform.system(),
        }

    def _mkdir(self):
        for directory in ["bin", "etc", "share"]:
            path = os.path.join(self.context["prefix"], directory)

            self.logger.info("mkdir    %s", path)

            try:
                if os.path.exists(path):
                    if os.access(path, os.W_OK):
                        try:
                            self.logger.warning("mkdir    %s: exists, removing", path)
                            shutil.rmtree(path)
                        except:
                            self.logger.exception("mkdir    %s: can't remove dir", path)
                    else:
                        self.logger.error("mkdir    %s: can't create dir", path)

                os.makedirs(path, mode=0o755)
            except:
                self.logger.exception("mkdir    %s: can't create dir", path)

    def _render(self):
        template_loader = jinja2.FileSystemLoader("./utils")
        template_list = template_loader.list_templates()

        # clean platform blacklisted paths, if they exist
        if self.context["platform"] in self._PLATFORM_BLACKLIST:
            if self._PLATFORM_BLACKLIST[self.context["platform"]]:
                for path in self._PLATFORM_BLACKLIST[self.context["platform"]]:
                    template_list.remove(path)

        # create env
        template_env = jinja2.Environment(
            loader=template_loader,
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # render + write
        for path in template_list:
            # get write dest
            dest = os.path.join(self.context["prefix"], path)

            # render
            self.logger.info("template  %s", dest)
            template = template_env.get_template(path)
            result = template.render(self.context)

            # write
            try:
                with open(dest, "w", encoding="utf-8") as file:
                    file.write(result)
            except:
                self.logger.exception("template  %s: can't write", dest)

    def _symlinks(self):
        # setboxes symlinks
        if self.context["is_setboxes"]:
            self._ln(
                "/mnt/mss/stuff/techy-bits/git/setboxes",
                os.path.join(self.context["prefix"], "repo"),
            )
            self._ln(
                "/mnt/mss/stuff/techy-bits/work",
                os.path.join(self.context["prefix"], "work"),
            )

        # bash-handler symlinks
        bash_handler_symlinks = ["/etc/profile"]
        bash_handler_symlinks.append(
            "/etc/bash.bashrc" if self.context["platform"] == "Linux" else "/etc/bashrc"
        )
        for path in bash_handler_symlinks:
            self._ln(
                os.path.join(self.context["prefix"], "share", "bash-handler"), path
            )

    def _fixperms(self):
        chmod_list = []
        for root, dirs, files in os.walk("./utils"):
            for file in files:
                file_path = os.path.join(root, file)

                if os.access(file_path, os.X_OK):
                    realpath = os.path.join(
                        self.context["prefix"],
                        os.path.relpath(file_path, start="./utils"),
                    )

                    if os.path.exists(realpath):
                        self.logger.info("perms    %s", realpath)
                        os.chmod(realpath, os.stat(realpath).st_mode | 0o111)

    def run(self):
        self._set_root_logger()
        self.logger = logging.getLogger("OTG")

        self._parse_args()

        self._prompt()
        self._mkdir()
        self._render()
        self._symlinks()
        self._fixperms()


if __name__ == "__main__":
    temp_otg = TemplateOTG()
    temp_otg.run()
