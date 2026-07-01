from odoo import api, fields, models
from odoo.fields import Domain


class ResPartner(models.Model):
    _inherit = "res.partner"

    _rec_names_search = [
        "complete_name",
        "email",
        "ref",
        "vat",
        "company_registry",
        "ytk_partner_id",
    ]

    ytk_partner_id = fields.Char(
        string="Partner ID",
        copy=False,
        index="btree_not_null",
        help="Unique business identifier for this partner.",
    )

    _ytk_partner_id_unique = models.Constraint(
        "unique(ytk_partner_id)",
        "Partner ID must be unique.",
    )

    @api.model
    def name_search(self, name="", domain=None, operator="ilike", limit=100):
        domain = domain or []
        if not name:
            return super().name_search(name=name, domain=domain, operator=operator, limit=limit)

        partner_by_id = self.search(
            Domain.AND([domain, [("ytk_partner_id", operator, name)]]),
            limit=limit,
            order=self._order,
        )
        if limit and len(partner_by_id) >= limit:
            return [(partner.id, partner.display_name) for partner in partner_by_id]

        remaining_limit = max(limit - len(partner_by_id), 0) if limit else limit
        fallback_domain = domain
        if partner_by_id:
            fallback_domain = Domain.AND([domain, [("id", "not in", partner_by_id.ids)]])

        return [(partner.id, partner.display_name) for partner in partner_by_id] + super().name_search(
            name=name,
            domain=fallback_domain,
            operator=operator,
            limit=remaining_limit,
        )
