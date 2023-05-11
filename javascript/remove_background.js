
async function _remove_bg_send_to_inpaint(gallery) {
  switch_to_img2img_tab(4);
  
  console.log(gallery);
  const dataURL = gallery[0].data;
  console.log(dataURL);
  
  const blob = await (await fetch(dataURL)).blob()
  const dt = new DataTransfer();
  dt.items.add(new File([blob], "ImageBrowser.png", { type: blob.type }));
  
  let inpaint_image_input = gradioApp().getElementById('img_inpaint_base').querySelector("input[type='file']");
  inpaint_image_input.files = dt.files;
  inpaint_image_input.value = "";
  inpaint_image_input.dispatchEvent(new Event("change", { bubbles: true, composed: true }));
  
}


function remove_bg_send_to_inpaint(gallery) {
  _remove_bg_send_to_inpaint(gallery);
  return args_to_array(arguments);
}
