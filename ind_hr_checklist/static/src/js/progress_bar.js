/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

console.log("✅ ProgressBarField component loaded");

export class ProgressBarField extends Component {
    static template = "IndHrChecklist.ProgressBar";
    
    setup() {
        console.log("✅ ProgressBarField initialized with value:", this.props.value);
    }

    get progressBarClass() {
        const value = this.props.value || 0;
        console.log("🔄 Calculating progress bar class for value:", value);
        
        if (value < 50) return 'bg-danger';
        if (value >= 50 && value < 80) return 'bg-warning';
        return 'bg-success';
    }
}

ProgressBarField.props = {
    ...standardFieldProps,
};

export const progressBarField = {
    component: ProgressBarField,
};

registry.category("fields").add("document_completion", progressBarField);
console.log("✅ ProgressBarField registered as 'document_completion'");