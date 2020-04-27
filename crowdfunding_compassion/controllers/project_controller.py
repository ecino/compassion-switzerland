from datetime import datetime

from babel.dates import format_timedelta

from odoo.http import request, route, Controller
from odoo.addons.cms_form.controllers.main import FormControllerMixin
from odoo.addons.cms_form_compassion.controllers.payment_controller import (
    PaymentFormController,
)


class ProjectController(PaymentFormController, FormControllerMixin):

    # Demo route used to display demo project
    # TODO: Remove when developmnent is done
    @route("/project/demo", auth="public", website=True)
    def demo_project_page(self, **kwargs):
        demo_project = request.env.ref(
            "crowdfunding_compassion.demo_project_crowdfunding"
        ).sudo()

        return request.render(
            "crowdfunding_compassion.project_page",
            self._prepare_project_values(demo_project, **kwargs),
        )

    @route(
        ["/project/<model('crowdfunding.project'):project>"],
        auth="public",
        website=True,
    )
    def project_page(self, project, **kwargs):
        # Get project with sudo, otherwise some parts will be blocked from public
        # access, for example res.partner or account.invoice.line. This is
        # simpler and less prone to error than defining custom access and
        # security rules for each of them.
        return request.render(
            "crowdfunding_compassion.project_page",
            self._prepare_project_values(project.sudo(), **kwargs),
        )

    # TODO: test when we can create data for a project
    def _prepare_project_values(self, project, **kwargs):
        sponsorships = [
            {
                "type": "sponsorship",
                "color": "blue",
                "text": f"{sponsorship.name} was sponsored",
                "image": sponsorship.child_id.portrait,
                "benefactor": sponsorship.correspondent_id.name,
                "date": sponsorship.activation_date,
                "time_ago": get_time_ago(sponsorship.activation_date),
            }
            for sponsorship in project.sponsorship_ids
        ]

        donations = [
            {
                "type": "donation",
                "color": "grey",
                "text": f"{donation.quantity} {donation.product_id.name} built",
                "image": "TODO: fund icon selector",
                "benefactor": donation.invoice_id.partner_id.name,
                "date": donation.invoice_id.date_invoice,
                "time_ago": get_time_ago(donation.invoice_id.date_invoice),
            }
            for donation in project.invoice_line_ids
        ]

        # Chronological list of sponsorships and fund donations for impact display
        impact = sorted(sponsorships + donations, key=lambda x: x["date"])

        return {"project": project, "impact": impact}

    # To preselect a participant, pass its id as particpant query parameter
    @route(
        ["/project/<model('crowdfunding.project'):project>/donation"],
        auth="public",
        website=True,
    )
    def project_donation_page(self, project, **kwargs):
        participant = kwargs.get("participant")

        return request.render(
            "crowdfunding_compassion.project_donation_page",
            {"project": project.sudo(), "selected_participant": participant},
        )

    @route(
        [
            "/project/<model('crowdfunding.project'):project>/donation/form/<model('crowdfunding.participant'):participant>"
        ],
        auth="public",
        website=True,
    )
    def project_donation_form_page(self, project, participant, **kwargs):
        kwargs["form_model_key"] = "cms.form.crowdfunding.donation"

        donation_form = self.get_form(False, **kwargs)
        donation_form.form_process()

        context = {
            "project": project.sudo(),
            "participant": participant.sudo(),
            "form": donation_form.sudo(),
            "main_object": project.sudo(),
        }

        # if donation_form.form_success:
        #     # The user submitted a donation, redirect to confirmation
        #     return werkzeug.utils.redirect(donation_form.form_next_url(), code=303)

        return request.render(
            "crowdfunding_compassion.project_donation_form_page", context,
        )


# Utils
def get_time_ago(date):
    return format_timedelta(datetime.now() - date, add_direction=True, locale="en")
