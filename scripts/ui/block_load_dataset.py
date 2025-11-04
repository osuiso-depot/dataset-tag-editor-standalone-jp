from __future__ import annotations
from typing import TYPE_CHECKING, Callable
import gradio as gr

import settings
import cmd_args
from .ui_common import *
from .uibase import UIBase
from scripts.ui.i18n_helper import t

if TYPE_CHECKING:
    from .ui_classes import *


class LoadDatasetUI(UIBase):

    def create_ui(self, cfg_general):
        with gr.Column(variant="panel"):
            with gr.Row():
                with gr.Column(scale=3):
                    self.tb_img_directory = gr.Textbox(
                        label=t("load_dataset.dataset_directory.label"),
                        placeholder="C:\\directory\\of\\datasets",
                        value=cfg_general.dataset_dir,
                    )
                with gr.Column(scale=1, min_width=60):
                    self.tb_caption_file_ext = gr.Textbox(
                        label=t("load_dataset.caption_file_ext.label"),
                        placeholder=".txt (on Load and Save)",
                        value=cfg_general.caption_ext,
                    )
                with gr.Column(scale=1, min_width=80):
                    self.btn_load_datasets = gr.Button(value=t("load_dataset.load_button.label"))
                    self.btn_unload_datasets = gr.Button(value=t("load_dataset.unload_button.label"))
            with gr.Accordion(label=t("load_dataset.dataset_load_settings.label")):
                with gr.Row():
                    with gr.Column():
                        self.cb_load_recursive = gr.Checkbox(
                            value=cfg_general.load_recursive,
                            label=t("load_dataset.load_from_subdirectories.label"),
                        )
                        self.cb_load_caption_from_filename = gr.Checkbox(
                            value=cfg_general.load_caption_from_filename,
                            label=t("load_dataset.load_caption_from_filename.label"),
                        )
                        self.cb_replace_new_line_with_comma = gr.Checkbox(
                            value=cfg_general.replace_new_line,
                            label=t("load_dataset.replace_new_line_with_comma.label"),
                        )
                    with gr.Column():
                        interrogator_choices = [
                            (t("load_dataset.interrogator_choices.no"), "No"),
                            (t("load_dataset.interrogator_choices.if_empty"), "If Empty"),
                            (t("load_dataset.interrogator_choices.overwrite"), "Overwrite"),
                            (t("load_dataset.interrogator_choices.prepend"), "Prepend"),
                            (t("load_dataset.interrogator_choices.append"), "Append"),
                        ]

                        # 設定値がchoicesに存在しない場合のフォールバック
                        initial_interrogator_value = cfg_general.use_interrogator
                        if initial_interrogator_value not in [choice for choice in interrogator_choices]:
                            initial_interrogator_value = "No" # デフォルト値

                        self.rb_use_interrogator = gr.Radio(
                            choices=interrogator_choices,
                            value=initial_interrogator_value,
                            label=t("load_dataset.use_interrogator_caption.label"),
                            interactive=not cmd_args.opts.cpu_only,
                        )

                        # 設定値をフィルタリング（リストに含まれるもののみ）
                        valid_interrogators = [
                            name for name in (cfg_general.use_interrogator_names or [])
                            if name in dte_instance.INTERROGATOR_NAMES
                        ]

                        self.dd_interrogator_names = gr.Dropdown(
                            label=t("load_dataset.interrogators.label"),
                            choices=dte_instance.INTERROGATOR_NAMES,
                            value=valid_interrogators if valid_interrogators else None,
                            interactive=not cmd_args.opts.cpu_only,
                            multiselect=True,
                        )
            with gr.Accordion(label=t("load_dataset.interrogator_settings.label"), open=False):
                with gr.Row():
                    self.sl_custom_threshold_booru = gr.Slider(
                        minimum=0,
                        maximum=1,
                        value=cfg_general.custom_threshold_booru,
                        step=0.01,
                        interactive=not cmd_args.opts.cpu_only,
                        label=t("load_dataset.booru_score_threshold.label"),
                    )
                with gr.Row():
                    self.sl_custom_threshold_z3d = gr.Slider(
                        minimum=0,
                        maximum=1,
                        value=cfg_general.custom_threshold_z3d,
                        step=0.01,
                        interactive=not cmd_args.opts.cpu_only,
                        label=t("load_dataset.z3d_e621_score_threshold.label"),
                    )
                with gr.Row():
                    self.cb_use_custom_threshold_waifu = gr.Checkbox(
                        value=cfg_general.use_custom_threshold_waifu,
                        label=t("load_dataset.use_custom_threshold_waifu.label"),
                        interactive=not cmd_args.opts.cpu_only,
                    )
                    self.sl_custom_threshold_waifu = gr.Slider(
                        minimum=0,
                        maximum=1,
                        value=cfg_general.custom_threshold_waifu,
                        step=0.01,
                        interactive=not cmd_args.opts.cpu_only,
                        label=t("load_dataset.wdv14_tagger_score_threshold.label"),
                    )

    def set_callbacks(
        self,
        o_update_filter_and_gallery: list[gr.components.Component],
        toprow: ToprowUI,
        dataset_gallery: DatasetGalleryUI,
        filter_by_tags: FilterByTagsUI,
        filter_by_selection: FilterBySelectionUI,
        batch_edit_captions: BatchEditCaptionsUI,
        update_filter_and_gallery: Callable[[], list],
    ):
        def load_files_from_dir(
            dir: str,
            caption_file_ext: str,
            recursive: bool,
            load_caption_from_filename: bool,
            replace_new_line: bool,
            use_interrogator: str,
            use_interrogator_names: list[str],
            custom_threshold_booru: float,
            use_custom_threshold_waifu: bool,
            custom_threshold_waifu: float,
            custom_threshold_z3d: float,
            use_kohya_metadata: bool,
            kohya_json_path: str,
        ):
            interrogate_method = dte_instance.InterrogateMethod.NONE
            if use_interrogator == "If Empty":
                interrogate_method = dte_instance.InterrogateMethod.PREFILL
            elif use_interrogator == "Overwrite":
                interrogate_method = dte_instance.InterrogateMethod.OVERWRITE
            elif use_interrogator == "Prepend":
                interrogate_method = dte_instance.InterrogateMethod.PREPEND
            elif use_interrogator == "Append":
                interrogate_method = dte_instance.InterrogateMethod.APPEND

            threshold_booru = custom_threshold_booru
            threshold_waifu = custom_threshold_waifu if use_custom_threshold_waifu else -1
            threshold_z3d = custom_threshold_z3d

            dte_instance.load_dataset(
                dir,
                caption_file_ext,
                recursive,
                load_caption_from_filename,
                replace_new_line,
                interrogate_method,
                use_interrogator_names,
                threshold_booru,
                threshold_waifu,
                threshold_z3d,
                settings.current.use_temp_files,
                kohya_json_path if use_kohya_metadata else None,
                settings.current.max_resolution
            )
            imgs = dte_instance.get_filtered_imgs(filters=[])
            return (
                [imgs, []]
                + update_filter_and_gallery()
            )

        self.btn_load_datasets.click(
            fn=load_files_from_dir,
            inputs=[
                self.tb_img_directory,
                self.tb_caption_file_ext,
                self.cb_load_recursive,
                self.cb_load_caption_from_filename,
                self.cb_replace_new_line_with_comma,
                self.rb_use_interrogator,
                self.dd_interrogator_names,
                self.sl_custom_threshold_booru,
                self.cb_use_custom_threshold_waifu,
                self.sl_custom_threshold_waifu,
                self.sl_custom_threshold_z3d,
                toprow.cb_save_kohya_metadata,
                toprow.tb_metadata_output,
            ],
            outputs=[
                dataset_gallery.gl_dataset_images,
                filter_by_selection.gl_filter_images,
            ]
            + o_update_filter_and_gallery,
        )

        def unload_files():
            dte_instance.clear()
            return (
                [[], []]
                + filter_by_tags.clear_filters()
                + [batch_edit_captions.tag_select_ui_remove.cbg_tags_update()]
            )

        self.btn_unload_datasets.click(
            fn=unload_files,
            outputs=[
                dataset_gallery.gl_dataset_images,
                filter_by_selection.gl_filter_images,
            ]
            + filter_by_tags.clear_filters_output()
            + [batch_edit_captions.tag_select_ui_remove.cbg_tags]
        ).then(
            fn=lambda:update_filter_and_gallery(),
            outputs=o_update_filter_and_gallery
        )
