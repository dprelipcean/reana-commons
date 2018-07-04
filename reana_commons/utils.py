# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2018 CERN.
#
# REANA is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# REANA is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# REANA; if not, write to the Free Software Foundation, Inc., 59 Temple Place,
# Suite 330, Boston, MA 02111-1307, USA.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization or
# submit itself to any jurisdiction.
"""REANA commons utils."""

import hashlib
import json
import os

import fs

import click


def click_table_printer(headers, _filter, data):
    """Generate space separated output for click commands."""
    _filter = [h.lower() for h in _filter] + [h.upper() for h in _filter]
    headers = [h for h in headers if not _filter or h in _filter]
    # Maximum header width
    header_widths = [len(h) for h in headers]

    for row in data:
        for idx in range(len(headers)):
            # If a row contains an element which is wider update maximum width
            if header_widths[idx] < len(str(row[idx])):
                header_widths[idx] = len(str(row[idx]))
    # Prepare the format string with the maximum widths
    formatted_output_parts = ['{{:<{0}}}'.format(hw)
                              for hw in header_widths]
    formatted_output = '   '.join(formatted_output_parts)
    # Print the table with the headers capitalized
    click.echo(formatted_output.format(*[h.upper() for h in headers]))
    for row in data:
        click.echo(formatted_output.format(*row))


def get_user_analyses_dir(org, user):
    """Build the analyses directory path for certain user and organization.

    :param org: Organization which user is part of.
    :param user: Working directory owner.
    :return: Path to the user's analyses directory.
    """
    return fs.path.join(org, user, 'analyses')


def calculate_hash_of_dir(directory, verbose=0):
    """Calculate hash of directory."""
    SHAhash = hashlib.md5()
    if not os.path.exists(directory):
        return -1

    try:
        for root, dirs, files in os.walk(directory):
            for names in sorted(files):
                filepath = os.path.join(root, names)
                try:
                    f1 = open(filepath, 'rb')
                except Exception:
                    # You can't open the file for some reason
                    f1.close()
                    # We return -1 since we can not ensure that the file that
                    # can not be read will not change from one execution to
                    # another.
                    return -1
                while 1:
                    # Read file in as little chunks
                    buf = f1.read(4096)
                    if not buf:
                        break
                    SHAhash.update(hashlib.md5(buf).hexdigest().encode())
                f1.close()

    except Exception:
        return -1
    return SHAhash.hexdigest()


def calculate_job_input_hash(job_spec, workflow_json):
    """Calculate md5 hash of job specification and workflow json."""
    job_md5_buffer = hashlib.md5()
    job_md5_buffer.update(json.dumps(job_spec).encode('utf-8'))
    job_md5_buffer.update(json.dumps(workflow_json).encode('utf-8'))
    return job_md5_buffer.digest()
