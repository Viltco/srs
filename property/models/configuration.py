from odoo import api, fields, models, _


class PropertyType(models.Model):
    _name = "property.type"
    _description = "PropertyType"
    _rec_name = 'property_type'

    property_type = fields.Char(string='Property Type')


class MandateDetails(models.Model):
    _name = "mandate.details"
    _description = "MandateDetails"
    _rec_name = 'mandate_details'

    mandate_details = fields.Char(string='Mandate Details')


class AreaDetails(models.Model):
    _name = "area.details"
    _description = "Area"
    _rec_name = 'area_details'

    area_details = fields.Char(string='Area')


class FeatureAmenities(models.Model):
    _name = "feature.amenities"
    _description = "Feature"
    _rec_name = 'feature_amenities'

    feature_amenities = fields.Char(string='Feature Amenities')











