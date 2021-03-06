# -*- coding: utf-8 -*-
# Copyright (C) 2020 Greenbone Networks GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest

from selene.schema.relay import get_cursor

from selene.tests import GmpMockFactory

from selene.tests.utils.utils import (
    pluralize_name,
    compose_mock_command,
    return_gmp_methods,
)


def compose_mock_response(gmp_name):
    gmp_plural = pluralize_name(gmp_name)
    xml_response = f'''
        <get_{gmp_plural}_response>
                <{gmp_name} id="08b69003-5fc2-4037-a479-93b440211c73">
                    <name>a</name>
                </{gmp_name}>
                <{gmp_name} id="6b2db524-9fb0-45b8-9b56-d958f84cb546">
                    <name>b</name>
                </{gmp_name}>
                <{gmp_plural} start="1" max="10"/>
                <{gmp_name}_count>2<filtered>2</filtered>
                    <page>2</page>
                </{gmp_name}_count>
            </get_{gmp_plural}_response>
    '''
    return xml_response


def compose_mock_query(entity_plural):
    query = f'''
            query {{
                {entity_plural} (
                    filterString: "lorem rows=5 first=1",
                    after: "{get_cursor('abc', 123)}",
                    first: 10,
                ) {{
                    nodes {{
                        id
                    }}
                }}
            }}
            '''
    return query


def make_test_after_first(
    gmp_name: str,
    *,
    selene_name: str = None,
    gmp_cmd: str = None,
    plural_selene_name: str = None,
    **kwargs,
):

    if not selene_name:
        selene_name = gmp_name

    # for special gmp commands like "get_info_list"
    if not gmp_cmd:
        gmp_cmd = compose_mock_command(gmp_name)

    # for special plurals of irregulars like policy
    if not plural_selene_name:
        plural_selene_name = pluralize_name(selene_name)

    @unittest.mock.patch('selene.views.Gmp', new_callable=GmpMockFactory)
    def test(self, mock_gmp: GmpMockFactory):

        gmp_commands = return_gmp_methods(mock_gmp.gmp_protocol)

        mock_gmp.mock_response(gmp_cmd, compose_mock_response(gmp_name))

        self.login('foo', 'bar')

        response = self.query(compose_mock_query(plural_selene_name))

        json = response.json()

        self.assertResponseNoErrors(response)

        get_entities = gmp_commands[gmp_cmd]

        get_entities.assert_called_with(
            filter='lorem rows=10 first=125', **kwargs
        )

        entities = json['data'][plural_selene_name]['nodes']

        self.assertEqual(len(entities), 2)

    return test
