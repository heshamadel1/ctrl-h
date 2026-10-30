#!/bin/bash
# usage: bash run_asr.sh <name>   (needs <name>_vo.wav and <name>_segs.txt in $WORK; sherpa-onnx + whisper-small model in $SHERPA)
SHERPA=${SHERPA:-$HOME/sherpa}; WORK=${WORK:-$PWD}
cd "$SHERPA"
for n in "$@"; do
python3 -u "$(dirname "$0")/asr_seg.py" sherpa-onnx-whisper-small small "$WORK/${n}_vo.wav" "$WORK/${n}_segs.txt" > "$WORK/${n}_seg_asr.txt" 2>&1
done
