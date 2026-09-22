# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: lazy-import requests (chemistry extra)
"""PubChem API manager for Manim chemistry.

This module provides the PubchemAPIManager class for fetching molecular data from PubChem.

"""

from typing import Any, Optional, TYPE_CHECKING
import json
import time

from ...utils.deps import require

if TYPE_CHECKING:
    import requests


class PubchemAPIManager:
    """Manages the requests to the PubChem API to retrieve molecular data.

    Parameters
    ----------
    cid : :class:`int`, optional
        PubChem compound id of the molecule. Defaults to ``None``.
    name : :class:`str`, optional
        Name of the molecule. Defaults to ``None``.
    smiles : :class:`str`, optional
        SMILES identifier of the molecule. Defaults to ``None``.
    inchi : :class:`str`, optional
        InChI identifier of the molecule. Defaults to ``None``.
    three_d : :class:`bool`, optional
        Whether to retrieve the 3D structure of the molecule. Defaults to ``False``.
    format : :class:`str`, optional
        Format of the response data. Defaults to ``"json"``.
    """

    BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/"

    def __init__(
        self,
        cid: Optional[int] = None,
        name: Optional[str] = None,
        smiles: Optional[str] = None,
        inchi: Optional[str] = None,
        three_d: bool = False,
        format: str = "json",
    ):
        """Initialize the PubchemAPIManager instance."""
        if not any([cid, name, smiles, inchi]):
            raise Exception(
                "You should provide an identifier. Available identifiers are cid, name, smiles and inchi"
            )
        self.cid = cid
        self.name = name
        self.smiles = smiles
        self.inchi = inchi
        self.three_d = three_d
        self.format = format

    def handle_request(self, request: 'requests.models.Response', identifier: Any):
        """Validate a PubChem API response and return the decoded payload.

        Adds a small sleep after the request to avoid rate-limiting the PubChem API.

        Parameters
        ----------
        request : requests.Response
            The response object returned by the requests library.
        identifier
            The identifier used in the request (for error messages).

        Returns
        -------
        str
            JSON string of the response body, or the raw decoded content
            if JSON parsing fails.

        Raises
        ------
        Exception
            If the response status code is 404 (not found) or any other error.
        """
        requests = require("chemistry", "requests")
        # Added sleep to prevent overloading the PubChem API
        time.sleep(0.25)
        if request.status_code == 200:
            try:
                return json.dumps(request.json())

            except requests.exceptions.JSONDecodeError:
                return request.content.decode()

            except Exception as error:
                raise error

        if request.status_code == 404:
            raise Exception(f"Compound {identifier} not found")

        raise Exception(
            f"An error occurred when calling the Pub Chem API. Status code: {request.status_code}. Request response: {request.json}"
        )

    def from_cid(self):
        """Fetch molecule data from PubChem using the compound ID (CID)."""
        requests = require("chemistry", "requests")
        request_url = f"{PubchemAPIManager.BASE_URL}/cid/{self.cid}/{self.format}"
        if self.three_d:
            request_url += "?record_type=3d"

        request = requests.get(request_url)
        return self.handle_request(request=request, identifier=self.cid)

    def from_name(self):
        """Fetch molecule data from PubChem using the common name."""
        requests = require("chemistry", "requests")
        request_url = f"{PubchemAPIManager.BASE_URL}/name/{self.name}/{self.format}"
        if self.three_d:
            request_url += "?record_type=3d"

        request = requests.get(request_url)
        return self.handle_request(request=request, identifier=self.name)

    def from_smiles(self):
        """Fetch molecule data from PubChem using a SMILES string."""
        requests = require("chemistry", "requests")
        request_url = f"{PubchemAPIManager.BASE_URL}/smiles/{self.smiles}/{self.format}"
        if self.three_d:
            request_url += "?record_type=3d"

        request = requests.get(request_url)
        return self.handle_request(request=request, identifier=self.smiles)

    def from_inchi(self):
        """Fetch molecule data from PubChem using an InChI key."""
        requests = require("chemistry", "requests")
        request_url = (
            f"{PubchemAPIManager.BASE_URL}/inchikey/{self.inchi}/{self.format}"
        )
        if self.three_d:
            request_url += "?record_type=3d"

        request = requests.get(request_url)
        return self.handle_request(request=request, identifier=self.inchi)

    def get_molecule(self):
        """Dispatch to the correct ``from_*`` method based on the set identifier.

        Returns
        -------
        str
            Parsed molecule data as a JSON string.

        Raises
        ------
        Exception
            If no identifier has been set.
        """
        if self.cid:
            return self.from_cid()

        elif self.name:
            return self.from_name()

        elif self.smiles:
            return self.from_smiles()

        elif self.inchi:
            return self.from_inchi()

        else:
            raise Exception("No identifier provided")