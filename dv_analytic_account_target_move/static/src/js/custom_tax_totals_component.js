/** @odoo-module **/

import { registry } from "@web/core/registry";
import { TaxTotalsComponent } from "@account/components/tax_totals/tax_totals";

/**
 * Heredamos el TaxTotalsComponent
 */
export class CustomTaxTotalsComponent extends TaxTotalsComponent {
    _onChangeTaxValueByTaxGroup({ oldValue, newValue }) {
        if (oldValue === newValue) return;

        this.totals.display_rounding = false;

        let igvAmount = 0;

        for (const [_, groups] of Object.entries(this.totals.groups_by_subtotal)) {
            for (const group of groups) {
                if (group.tax_group_name === "IGV") {
                    igvAmount += group.tax_group_amount;
                }
            }
        }

        this.props.record.update({
            [this.props.name]: this.totals,
            manual_amount_tax: igvAmount,
        });
    }
}

// Registrar el nuevo componente en lugar del original
registry.category("fields").add("custom-account-tax-totals-field", {
    component: CustomTaxTotalsComponent,
});
