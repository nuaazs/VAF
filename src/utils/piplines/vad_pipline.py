
"""get vad result
    
    Args:
        file_mode (string): "url" or "file"

    Returns:
        json: response
    """
    spkid = request.form["spkid"]

    # STEP 1: Get wav file.
    if file_mode == "file":
        new_file = request.files["wav_file"]
        filepath, _ = save_file(file=new_file, spk=spkid)
    elif file_mode == "url":
        new_url = request.form.get("wav_url")
        filepath, _ = save_url(url=new_url, spk=spkid)

    # STEP 1.5: Resample wav file.
    wav = resample(wav_filepath=filepath, action_type=None)

    # STEP 2: VAD
    vad_result = vad(wav=wav, spkid=spkid)
    os.makedirs(f"/tmp/output_vad", exist_ok=True)
    torchaudio.save(f"/tmp/output_vad/{spkid}.wav", vad_result['wav_torch'].reshape(1, -1), cfg.SR)

    if "cuda" in cfg.DEVICE:
        torch.cuda.empty_cache()
    response = {'output_vad_file_path': f"/tmp/output_vad/{spkid}.wav"}