from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View

from bom.models import Part, PartClass, Subpart, SellerPart, Organization, Manufacturer, ManufacturerPart, User, UserMeta, PartRevision, Assembly, AssemblySubparts
from bom.third_party_apis.mouser import Mouser


class BomJsonResponse(View):
    response = {'errors': [], 'content': {}}


@method_decorator(login_required, name='dispatch')
class MouserPartMatchBOM(BomJsonResponse):
    def get(self, request, part_revision_id):
        part_revision = get_object_or_404(PartRevision, pk=part_revision_id)  # get all of the pricing for manufacturer parts, marked with mouser in this part

        # Goal is to search mouser for anything that we want from mouser, then update the part revision in the bom with that
        # To do that we can just get the manufacturer parts in this BOM
        part = part_revision.part
        qty_cache_key = str(part.id) + '_qty'
        assy_quantity = cache.get(qty_cache_key, 100)

        # TODO: For both flat_bom and indented_bom we will need to update each bom item's sourcing info
        # TODO: We will also need to udpate the bom summary info
        # TODO: We will also need to update the sourcing tab if the main part_revision is sourced from mouser
        flat_bom = part_revision.flat(assy_quantity)
        indented_bom = part_revision.indented(assy_quantity)

        mouser = Mouser()
        manufacturer_parts = flat_bom.mouser_parts()
        # Quantity is the same on flat and indented bom WRT sourcing, so we should only need to look up by part revision, or even part
        for bom_id, mp in manufacturer_parts.items():
            bom_part = flat_bom.parts[bom_id]
            bom_part_quantity = bom_part.total_extended_quantity
            part_seller_info = mouser.search_and_match(mp, quantity=bom_part_quantity)
            bom_part.seller_part = part_seller_info['optimal_seller_part']
            bom_part.api_info = part_seller_info['mouser_parts'][0]
            # TODO: add all seller parts

        # TODO: update indented BOM
        # for bom_id, bom_part in indented_bom.parts.items():

        flat_bom.update()
        self.response['content'].update({'flat_bom': flat_bom.as_dict()})
        return JsonResponse(self.response)
