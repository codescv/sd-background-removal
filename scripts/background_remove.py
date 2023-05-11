import gradio as gr
from rembg import remove
import PIL
import numpy as np
import torch
import requests
import random
from io import BytesIO
import os
import sys


import modules
from modules import paths, shared, script_callbacks, scripts, images
from modules.generation_parameters_copypaste import register_paste_params_button, ParamBinding


def get_alpha_mask(image, binary=False):
  image_arr = np.array(image)
  mask_arr = image_arr[:,:,-1]
  
  if binary:
    # force alpha to be 0 or 255
    mask_arr[np.where(mask_arr > 50)] = 255
    mask_arr[np.where(mask_arr <= 50)] = 0
  
  mask = PIL.Image.fromarray(mask_arr)
  return mask


def get_rembg_mask(image, binary=False):
  output = remove(image)
  img = np.array(output)
  mask_arr = 255-img[:, :, -1]

  if binary:
    # force alpha to be 0 or 255
    mask_arr[np.where(mask_arr > 50)] = 255
    mask_arr[np.where(mask_arr <= 50)] = 0
  
  mask = PIL.Image.fromarray(mask_arr, 'L')
  return mask


def get_mask(image, use_alpha=False, binary=False):
  if use_alpha:
    return get_alpha_mask(image, binary=binary)
  else:
    m_arr = np.array(image)

    if m_arr.shape[-1] == 4:
      # dealing with RGBA
      m_mask = m_arr[:, :, -1]
      x_range, y_range = np.where(m_mask == 255)
      x_min, x_max = np.min(x_range), np.max(x_range)
      y_min, y_max = np.min(y_range), np.max(y_range)

      # left, upper, right, and lower
      cropped_image = image.crop((y_min, x_min, y_max, x_max))
      cropped_mask = get_rembg_mask(cropped_image, binary=binary)
      padded_mask = np.pad(cropped_mask, [(x_min, image.size[1]-x_max), (y_min, image.size[0]-y_max)], mode='constant', constant_values=255)
      padded_mask_image = PIL.Image.fromarray(padded_mask, 'L')
      return padded_mask_image
    
    return get_rembg_mask(image, binary=binary)


def remove_background(image, use_alpha_channel, binary):
  return [image, get_mask(image)]


def on_ui_tabs():

  with gr.Blocks(analytics_enabled=False) as remove_background_ui:
    with gr.Row():
      with gr.Column():
        gr.Markdown('Input')

        with gr.Box():
          with gr.Column():
            image = gr.Image(label='image', type = 'pil', image_mode='RGBA', tool='editor')
            remove_bg_button = gr.Button(value="Remove Background")

        use_alpha_channel = gr.Checkbox(label="Use Transparency Channel from Image(PNG)", info="Use Transparency Channel from Image(PNG)", value=False)
        binary = gr.Checkbox(label="Force Binary Mask(0 or 255)", info="Force Binary Mask(0 or 255)", value=False)

      with gr.Column():
        gr.Markdown('Output')
        image_output = gr.Gallery(label="Output", id='remove_bg_output').style(grid=[3], height=768)
        
        # send_to_inpaint_button = gr.Button(value="Send to Inpaint")

    remove_bg_button.click(
        remove_background,
        inputs=[image, use_alpha_channel, binary],
        outputs=image_output
    )
    
    # register_paste_params_button(ParamBinding(paste_button=send_to_inpaint_button, tabname='inpaint', source_text_component=None, source_image_component=image_output, source_tabname=None))

  return (remove_background_ui , "Remove Background", "remove_background"),


script_callbacks.on_ui_tabs(on_ui_tabs)