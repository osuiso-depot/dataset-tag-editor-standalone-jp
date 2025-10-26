from __future__ import annotations
from typing import TYPE_CHECKING, Callable
import gradio as gr

from .ui_common import *
from .uibase import UIBase
from .block_tag_select import TagSelectUI
from scripts.ui.i18n_helper import t

if TYPE_CHECKING:
    from .ui_classes import *

SortBy = dte_instance.SortBy
SortOrder = dte_instance.SortOrder


class BatchEditCaptionsUI(UIBase):
    def __init__(self):
        self.tag_select_ui_remove = TagSelectUI()
        self.show_only_selected_tags = False

    def create_ui(
        self, cfg_batch_edit, get_filters: Callable[[], list[dte_module.filters.Filter]]
    ):
        with gr.Tab(label=t("batch_edit.search_and_replace_tab.label")):
            with gr.Column(variant="panel"):
                gr.HTML(t("batch_edit.edit_common_tags.html"))
                self.cb_show_only_tags_selected = gr.Checkbox(
                    value=cfg_batch_edit.show_only_selected,
                    label=t("batch_edit.show_only_tags_selected.label"),
                )
                self.show_only_selected_tags = cfg_batch_edit.show_only_selected
                self.tb_common_tags = gr.Textbox(label=t("batch_edit.common_tags.label"), interactive=False)
                self.tb_edit_tags = gr.Textbox(label=t("batch_edit.edit_tags.label"), interactive=True)
                self.cb_prepend_tags = gr.Checkbox(
                    value=cfg_batch_edit.prepend, label=t("batch_edit.prepend_additional_tags.label")
                )
                self.btn_apply_edit_tags = gr.Button(
                    value=t("batch_edit.apply_changes_to_filtered_images.label"), variant="primary"
                )
                with gr.Accordion(
                    label=t("batch_edit.show_description_of_how_to_edit_tags.label"), open=False
                ):
                    gr.HTML(
                        value=t("batch_edit.edit_tags_description.html")
                    )
            with gr.Column(variant="panel"):
                gr.HTML(t("batch_edit.search_and_replace_for_all_images_displayed.html"))
                self.tb_sr_search_tags = gr.Textbox(
                    label=t("batch_edit.search_text.label"), interactive=True
                )
                self.tb_sr_replace_tags = gr.Textbox(
                    label=t("batch_edit.replace_text.label"), interactive=True
                )
                self.cb_use_regex = gr.Checkbox(
                    label=t("batch_edit.use_regex.label"), value=cfg_batch_edit.use_regex
                )
                self.rb_sr_replace_target = gr.Radio(
                    [t("batch_edit.replace_target.only_selected_tags"), t("batch_edit.replace_target.each_tags"), t("batch_edit.replace_target.entire_caption")],
                    value=cfg_batch_edit.target,
                    label=t("batch_edit.search_and_replace_in.label"),
                    interactive=True,
                )
                self.tb_sr_selected_tags = gr.Textbox(
                    label=t("batch_edit.selected_tags.label"), interactive=False, lines=2
                )
                self.btn_apply_sr_tags = gr.Button(
                    value=t("batch_edit.search_and_replace_button.label"), variant="primary"
                )
        with gr.Tab(label=t("batch_edit.remove_tab.label")):
            with gr.Column(variant="panel"):
                gr.HTML(t("batch_edit.remove_duplicate_tags_html"))
                self.btn_remove_duplicate = gr.Button(
                    value=t("batch_edit.remove_duplicate_tags_button.label"), variant="primary"
                )
            with gr.Column(variant="panel"):
                gr.HTML(t("batch_edit.remove_selected_tags_html"))
                self.btn_remove_selected = gr.Button(
                    value=t("batch_edit.remove_selected_tags_button.label"), variant="primary"
                )
                self.tag_select_ui_remove.create_ui(
                    get_filters,
                    cfg_batch_edit.sory_by,
                    cfg_batch_edit.sort_order,
                    cfg_batch_edit.sw_prefix,
                    cfg_batch_edit.sw_suffix,
                    cfg_batch_edit.sw_regex,
                )
        with gr.Tab(label=t("batch_edit.extras_tab.label")):
            with gr.Column(variant="panel"):
                gr.HTML(t("batch_edit.sort_tags_html"))
                with gr.Row():
                    self.rb_sort_by = gr.Radio(
                        choices=[e.value for e in SortBy],
                        value=cfg_batch_edit.batch_sort_by,
                        interactive=True,
                        label=t("batch_edit.sort_by.label"),
                    )
                    self.rb_sort_order = gr.Radio(
                        choices=[e.value for e in SortOrder],
                        value=cfg_batch_edit.batch_sort_order,
                        interactive=True,
                        label=t("batch_edit.sort_order.label"),
                    )
                self.btn_sort_selected = gr.Button(value=t("batch_edit.sort_tags_button.label"), variant="primary")
            with gr.Column(variant="panel"):
                gr.HTML(t("batch_edit.truncate_tags_html"))
                self.nb_token_count = gr.Number(
                    value=cfg_batch_edit.token_count, precision=0
                )
                self.btn_truncate_by_token = gr.Button(
                    value=t("batch_edit.truncate_tags_by_token_count_button.label"), variant="primary"
                )

    def set_callbacks(
        self,
        o_update_filter_and_gallery: list[gr.components.Component],
        load_dataset: LoadDatasetUI,
        filter_by_tags: FilterByTagsUI,
        get_filters: Callable[[], list[dte_module.filters.Filter]],
        update_filter_and_gallery: Callable[[], list],
    ):
        load_dataset.btn_load_datasets.click(
            fn=lambda: ["", ""], outputs=[self.tb_common_tags, self.tb_edit_tags]
        )

        def apply_edit_tags(search_tags: str, replace_tags: str, prepend: bool):
            search_tags = [t.strip() for t in search_tags.split(",")]
            search_tags = [t for t in search_tags if t]
            replace_tags = [t.strip() for t in replace_tags.split(",")]
            replace_tags = [t for t in replace_tags if t]

            dte_instance.replace_tags(
                search_tags=search_tags,
                replace_tags=replace_tags,
                filters=get_filters(),
                prepend=prepend,
            )
            filter_by_tags.tag_filter_ui.get_filter().tags = (
                dte_instance.get_replaced_tagset(
                    filter_by_tags.tag_filter_ui.get_filter().tags,
                    search_tags,
                    replace_tags,
                )
            )
            filter_by_tags.tag_filter_ui_neg.get_filter().tags = (
                dte_instance.get_replaced_tagset(
                    filter_by_tags.tag_filter_ui_neg.get_filter().tags,
                    search_tags,
                    replace_tags,
                )
            )

            return update_filter_and_gallery()

        self.btn_apply_edit_tags.click(
            fn=apply_edit_tags,
            inputs=[self.tb_common_tags, self.tb_edit_tags, self.cb_prepend_tags],
            outputs=o_update_filter_and_gallery,
        )
        self.btn_apply_edit_tags.click(
            fn=None, js="() => gl_dataset_images_close()"
        )

        def search_and_replace(
            search_text: str, replace_text: str, target_text: str, use_regex: bool
        ):
            if target_text == "Only Selected Tags":
                selected_tags = set(filter_by_tags.tag_filter_ui.selected_tags)
                dte_instance.search_and_replace_selected_tags(
                    search_text=search_text,
                    replace_text=replace_text,
                    selected_tags=selected_tags,
                    filters=get_filters(),
                    use_regex=use_regex,
                )
                filter_by_tags.tag_filter_ui.filter.tags = (
                    dte_instance.search_and_replace_tag_set(
                        search_text,
                        replace_text,
                        filter_by_tags.tag_filter_ui.filter.tags,
                        selected_tags,
                        use_regex,
                    )
                )
                filter_by_tags.tag_filter_ui_neg.filter.tags = (
                    dte_instance.search_and_replace_tag_set(
                        search_text,
                        replace_text,
                        filter_by_tags.tag_filter_ui_neg.filter.tags,
                        selected_tags,
                        use_regex,
                    )
                )

            elif target_text == "Each Tags":
                dte_instance.search_and_replace_selected_tags(
                    search_text=search_text,
                    replace_text=replace_text,
                    selected_tags=None,
                    filters=get_filters(),
                    use_regex=use_regex,
                )
                filter_by_tags.tag_filter_ui.filter.tags = (
                    dte_instance.search_and_replace_tag_set(
                        search_text,
                        replace_text,
                        filter_by_tags.tag_filter_ui.filter.tags,
                        None,
                        use_regex,
                    )
                )
                filter_by_tags.tag_filter_ui_neg.filter.tags = (
                    dte_instance.search_and_replace_tag_set(
                        search_text,
                        replace_text,
                        filter_by_tags.tag_filter_ui_neg.filter.tags,
                        None,
                        use_regex,
                    )
                )

            elif target_text == "Entire Caption":
                dte_instance.search_and_replace_caption(
                    search_text=search_text,
                    replace_text=replace_text,
                    filters=get_filters(),
                    use_regex=use_regex,
                )
                filter_by_tags.tag_filter_ui.filter.tags = (
                    dte_instance.search_and_replace_tag_set(
                        search_text,
                        replace_text,
                        filter_by_tags.tag_filter_ui.filter.tags,
                        None,
                        use_regex,
                    )
                )
                filter_by_tags.tag_filter_ui_neg.filter.tags = (
                    dte_instance.search_and_replace_tag_set(
                        search_text,
                        replace_text,
                        filter_by_tags.tag_filter_ui_neg.filter.tags,
                        None,
                        use_regex,
                    )
                )

            return update_filter_and_gallery()

        self.btn_apply_sr_tags.click(
            fn=search_and_replace,
            inputs=[
                self.tb_sr_search_tags,
                self.tb_sr_replace_tags,
                self.rb_sr_replace_target,
                self.cb_use_regex,
            ],
            outputs=o_update_filter_and_gallery,
        )
        self.btn_apply_sr_tags.click(
            fn=None, js="() => gl_dataset_images_close()"
        )

        def cb_show_only_tags_selected_changed(value: bool):
            self.show_only_selected_tags = value
            return self.get_common_tags(get_filters, filter_by_tags)

        self.cb_show_only_tags_selected.change(
            fn=cb_show_only_tags_selected_changed,
            inputs=self.cb_show_only_tags_selected,
            outputs=[self.tb_common_tags, self.tb_edit_tags],
        )

        def remove_duplicated_tags():
            dte_instance.remove_duplicated_tags(get_filters())
            return update_filter_and_gallery()

        self.btn_remove_duplicate.click(
            fn=remove_duplicated_tags, outputs=o_update_filter_and_gallery
        )

        self.tag_select_ui_remove.set_callbacks()

        def remove_selected_tags():
            dte_instance.remove_tags(
                self.tag_select_ui_remove.selected_tags, get_filters()
            )
            return update_filter_and_gallery()

        self.btn_remove_selected.click(
            fn=remove_selected_tags, outputs=o_update_filter_and_gallery
        )

        def sort_selected_tags(sort_by: str, sort_order: str):
            sort_by = SortBy(sort_by)
            sort_order = SortOrder(sort_order)
            dte_instance.sort_filtered_tags(
                get_filters(), sort_by=sort_by, sort_order=sort_order
            )
            return update_filter_and_gallery()

        self.btn_sort_selected.click(
            fn=sort_selected_tags,
            inputs=[self.rb_sort_by, self.rb_sort_order],
            outputs=o_update_filter_and_gallery,
        )

        self.cb_show_only_tags_selected.change(
            fn=self.func_to_set_value("show_only_selected_tags"),
            inputs=self.cb_show_only_tags_selected,
        )

        def truncate_by_token_count(token_count: int):
            token_count = max(int(token_count), 0)
            dte_instance.truncate_filtered_tags_by_token_count(
                get_filters(), token_count
            )
            return update_filter_and_gallery()

        self.btn_truncate_by_token.click(
            fn=truncate_by_token_count,
            inputs=self.nb_token_count,
            outputs=o_update_filter_and_gallery,
        )

    def get_common_tags(
        self,
        get_filters: Callable[[], list[dte_module.filters.Filter]],
        filter_by_tags: FilterByTagsUI,
    ):
        if self.show_only_selected_tags:
            tags = ", ".join(
                [
                    t
                    for t in dte_instance.get_common_tags(filters=get_filters())
                    if t in filter_by_tags.tag_filter_ui.filter.tags
                ]
            )
        else:
            tags = ", ".join(dte_instance.get_common_tags(filters=get_filters()))
        return [tags, tags]
