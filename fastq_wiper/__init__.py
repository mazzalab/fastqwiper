""""
File description
"""

import logging
from fastq_wiper.color_log_formatter import ColorFormatter

__author__ = "Tommaso Mazza"
__copyright__ = "Copyright 2020, The FastqWiper Project"
__version__ = "0.0.1"
__maintainer__ = "Tommaso Mazza"
__email__ = "bioinformatics@css-mendel.it"
__status__ = "Development"
__date__ = "28/12/2020"
__creator__ = "t.mazza"
__license__ = u"""
  Copyright (C) 2020 Tommaso Mazza <t.mazza@css-mendel.it>
  Viale Regina Margherita 261, 00198 Rome, Italy

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc.,  51 Franklin Street, Fifth Floor, Boston, MA
  02110-1301 USA
  """

# logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
# logging.getLogger(__name__).addHandler(logging.NullHandler())
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# DEBUGFORMATTER = '%(filename)s:%(name)s:%(funcName)s:%(lineno)d: %(message)s'
DEBUGFORMATTER = '%(asctime)s - %(name)s/%(filename)s(%(funcName)s) - %(levelname)s - %(message)s'
"""Debug file formatter."""

# defines the stream handler
ch = logging.StreamHandler()  # creates the handler
ch.setLevel(logging.INFO)  # sets the handler info
cf = ColorFormatter(DEBUGFORMATTER)
ch.setFormatter(cf)  # sets the handler formatting

# adds the handler to the global variable: log
log.addHandler(ch)