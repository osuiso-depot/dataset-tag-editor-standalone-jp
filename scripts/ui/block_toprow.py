from __future__ import annotations
from typing import TYPE_CHECKING
import gradio as gr

from .ui_common import *
from .uibase import UIBase
from scripts.ui.i18n_helper import t

if TYPE_CHECKING:
    from .ui_classes import *


class ToprowUI(UIBase):
    def create_ui(self, cfg_general):
        with gr.Column(variant="panel"):
            with gr.Row():
                with gr.Column(scale=1):
                    self.btn_save_all_changes = gr.Button(
                        value=t("toprow.save_all_changes.label"), variant="primary"
                    )
                with gr.Column(scale=2):
                    self.cb_backup = gr.Checkbox(
                        value=cfg_general.backup,
                        label=t("toprow.backup_original_text_file.label"),
                        interactive=True,
                    )
            gr.HTML(
                value=t("toprow.new_text_file_note.label")
            )
            with gr.Row():
                self.cb_save_kohya_metadata = gr.Checkbox(
                    value=cfg_general.save_kohya_metadata,
                    label=t("toprow.use_kohya_metadata.label"),
                    interactive=True,
                )
            with gr.Row():
                with gr.Column(
                    variant="panel", visible=cfg_general.save_kohya_metadata
                ) as self.cl_kohya_metadata:
                    self.tb_metadata_output = gr.Textbox(
                        label=t("toprow.metadata_output_path.label"),
                        placeholder="C:\\path\\to\\metadata.json",
                        value=cfg_general.meta_output_path,
                    )
                    self.tb_metadata_input = gr.Textbox(
                        label=t("toprow.metadata_input_path.label"),
                        placeholder="C:\\path\\to\\metadata.json",
                        value=cfg_general.meta_input_path,
                    )
                    with gr.Row():
                        self.cb_metadata_overwrite = gr.Checkbox(
                            value=cfg_general.meta_overwrite,
                            label=t("toprow.metadata_overwrite.label"),
                            interactive=True,
                        )
                        self.cb_metadata_as_caption = gr.Checkbox(
                            value=cfg_general.meta_save_as_caption,
                            label=t("toprow.metadata_save_as_caption.label"),
                            interactive=True,
                        )
                        self.cb_metadata_use_fullpath = gr.Checkbox(
                            value=cfg_general.meta_use_full_path,
                            label=t("toprow.metadata_use_fullpath.label"),
                            interactive=True,
                        )
            with gr.Row(visible=False):
                self.txt_result = gr.Textbox(label=t("toprow.results.label"), interactive=False)

    def set_callbacks(self, load_dataset: LoadDatasetUI):
        def save_all_changes(
            backup: bool,
            save_kohya_metadata: bool,
            metadata_output: str,
            metadata_input: str,
            metadata_overwrite: bool,
            metadata_as_caption: bool,
            metadata_use_fullpath: bool,
            caption_file_ext: str
        ):
            if not metadata_input:
                metadata_input = None
            dte_instance.save_dataset(
                backup,
                caption_file_ext,
                save_kohya_metadata,
                metadata_output,
                metadata_input,
                metadata_overwrite,
                metadata_as_caption,
                metadata_use_fullpath,
            )

        self.btn_save_all_changes.click(
            fn=save_all_changes,
            inputs=[
                self.cb_backup,
                self.cb_save_kohya_metadata,
                self.tb_metadata_output,
                self.tb_metadata_input,
                self.cb_metadata_overwrite,
                self.cb_metadata_as_caption,
                self.cb_metadata_use_fullpath,
                load_dataset.tb_caption_file_ext
            ],
        )

        self.cb_save_kohya_metadata.change(
            fn=lambda x: gr.update(visible=x),
            inputs=self.cb_save_kohya_metadata,
            outputs=self.cl_kohya_metadata,
        )
