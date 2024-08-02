# -*- coding: utf-8 -*-
"""
SEED Platform (TM), Copyright (c) Alliance for Sustainable Energy, LLC, and other contributors.
See also https://github.com/seed-platform/seed/main/LICENSE.md
"""

from django.core.management.base import BaseCommand
from seed.data_importer.models import ImportFile
from botocore.exceptions import ClientError


class Command(BaseCommand):
    help = 'Remove /seed added to dwonload url for HELIX uploaded files'

    def handle(self, *args, **options):
        files = ImportFile.objects.all()
        for f in files:
            try:
                if "/seed/" in f.file.name:
                    new_file_name = str(f.file.name).replace("/seed/", "")
                    f.file.name = new_file_name
                    f.save()
            except (ClientError, FileNotFoundError) as error:
                print("File not found, not renaming the file:", error)
                

