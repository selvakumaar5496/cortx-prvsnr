#
# Copyright (c) 2020 Seagate Technology LLC and/or its Affiliates
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.
#
#
# Cortx Setup API to create a storageset


from ..command import Command
from cortx_setup.config import CONFSTORE_CLUSTER_FILE
from cortx_setup.commands.common_utils import (
    get_cluster_id
)
from provisioner.commands import PillarSet
from provisioner.salt import local_minion_id
from cortx.utils.conf_store import Conf


class CreateStorageSet(Command):
    _args = {
        'name': {
          'type': str,
          'default': 'storage-set-1',
          'optional': True
        },
        'count': {
          'type': int,
          'default': 1,
          'optional': True
        }
    }

    def run(self, name=None, count=None):
        try:
            node_id = local_minion_id()
            index = 'storage_create_index'

            # TODO: Addnl validation needed. Support for updating
            # values for multiple storagesets in a cluster.

            self.load_conf_store(
                index,
                f'json://{CONFSTORE_CLUSTER_FILE}'
            )
            cluster_id = get_cluster_id()
            self.logger.debug(
                f"Updating storageset '{name}' with "
                f"node count '{count}' in ConfStore"
            )

            PillarSet().run(
                'cluster/storage_set/name',
                name
            )

            #Not updating node count to Confstore
            #TODO: Handle scenario for multiple storagesets
            PillarSet().run(
                'cluster/storage_set/count',
                count
            )

            try:
                tot_storageset = Conf.get (
                    'storage_create_index',
                    f'cluster>{cluster_id}>storage_set'
                )
                storage_set_index = len(tot_storageset)
            except Exception:
                self.logger.debug(
                    "No storage_set in confstore, setting storage_set_index to 0"
                    )
                storage_set_index = 0

            Conf.set(
                index,
                f'cluster>{cluster_id}>storage_set[{storage_set_index}]>name',
                name
            )

            Conf.save(index)

        except ValueError as exc:
            raise ValueError(
              f"Failed to create Storageset: {str(exc)}"
            )
