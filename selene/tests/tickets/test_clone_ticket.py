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

from unittest.mock import patch

from selene.tests import SeleneTestCase, GmpMockFactory


@patch('selene.views.Gmp', new_callable=GmpMockFactory)
class CloneTicketTestCase(SeleneTestCase):
    def test_require_authentication(self, _mock_gmp: GmpMockFactory):
        response = self.query(
            '''
            mutation {
                cloneTicket(id: "e1438fb2-ab2c-4f4a-ad6b-de97005256e8") {
                    id
                }
            }
            '''
        )

        self.assertResponseAuthenticationRequired(response)

    def test_clone_ticket(self, mock_gmp: GmpMockFactory):
        mock_gmp.mock_response(
            'clone_ticket',
            '''
            <create_ticket_response status="201" status_text="OK,
             resource created" id="e1438fb2-ab2c-4f4a-ad6c-de97005256e8"/>
            ''',
        )

        self.login('foo', 'bar')

        response = self.query(
            '''
            mutation {
                cloneTicket(id: "e1438fb2-ab2c-4f4a-ad6b-de97005256e8") {
                    id
                }
            }
            '''
        )

        json = response.json()

        self.assertResponseNoErrors(response)

        ticket_id = json['data']['cloneTicket']['id']

        self.assertEqual(ticket_id, 'e1438fb2-ab2c-4f4a-ad6c-de97005256e8')
