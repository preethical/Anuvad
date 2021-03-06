#
# Copyright © 2012 - 2020 Michal Čihař <michal@cihar.com>
#
# This file is part of Weblate <https://weblate.org/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

from weblate.machinery.base import MachineTranslation
from weblate.memory.models import Memory
from weblate.utils.search import Comparer


class WeblateMemory(MachineTranslation):
    """Translation service using strings already translated in Weblate."""

    name = "Weblate Translation Memory"
    rank_boost = 2
    cache_translations = False

    def convert_language(self, language):
        """No conversion of language object."""
        return language

    def is_supported(self, source, language):
        """Any language is supported."""
        return True

    def download_translations(self, source, language, text, unit, user, search):
        """Download list of possible translations from a service."""
        comparer = Comparer()
        for result in Memory.objects.lookup(
            source,
            language,
            text,
            user,
            unit.translation.component.project,
            unit.translation.component.project.use_shared_tm,
        ).iterator():
            quality = comparer.similarity(text, result.source)
            if quality < 10 or (quality < 75 and not search):
                continue
            yield {
                "text": result.target,
                "quality": quality,
                "service": self.name,
                "origin": result.get_origin_display(),
                "source": result.source,
            }
