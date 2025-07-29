
import logging
from googleads import ad_manager

from Openwrap_DFP_Setup.dfp.client import get_client


logger = logging.getLogger(__name__)

def make_licas(line_item_ids, creative_ids, size_overrides=[], setup_type= None, slot=None,durations=None):
  """
  Attaches creatives to line items in DFP.

  Args:
    line_item_ids (arr): an array of line item IDs
    creative_ids (arr): an array of creative IDs
    slot(string): slot name in case of setup_type = ADPOD
    durations(int array): creative durations for ADPOD.
  Returns:
    None
  """
  dfp_client = get_client()
  lica_service = dfp_client.GetService(
    'LineItemCreativeAssociationService', version='v202502')

  sizes = []

  for size_override in size_overrides:
    sizes.append(size_override)

  licas = []

  #set creativeSetId for video line items
  if setup_type in ('JWPLAYER', 'VIDEO', 'IN_APP_VIDEO'):
    for line_item_id in line_item_ids:
      for creative_id in creative_ids:
        licas.append({
          'creativeSetId': creative_id,
          'lineItemId': line_item_id,
          'sizes': sizes
        })
  elif setup_type == 'ADPOD':
    for line_item_id in line_item_ids:
      for i in range(len(creative_ids)):
        licas.append({
          'creativeSetId': creative_ids[i],
          'lineItemId': line_item_id,
          'sizes': sizes,
          'targetingName':"{}_{}second_ad".format(slot,durations[i])
        })      
  else:
    for line_item_id in line_item_ids:
      for creative_id in creative_ids:
        licas.append({
          'creativeId': creative_id,
          'lineItemId': line_item_id,
          # "Overrides the value set for Creative.size, which allows the
          #   creative to be served to ad units that would otherwise not be
          #   compatible for its actual size."
          #    https://developers.google.com/doubleclick-publishers/docs/reference/v201802/LineItemCreativeAssociationService.LineItemCreativeAssociation
          #
          # This is equivalent to selecting "Size overrides" in the DFP creative
          # settings, as recommended: http://prebid.org/adops/step-by-step.html
          'sizes': sizes
        })
  licas = lica_service.createLineItemCreativeAssociations(licas)

  if licas:
    logger.info(
      u'Created {0} line item <> creative associations.'.format(len(licas)))
  else:
    logger.info(u'No line item <> creative associations created.')
