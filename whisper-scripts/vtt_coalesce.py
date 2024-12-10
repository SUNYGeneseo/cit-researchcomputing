import argparse
import re

import webvtt, webvtt.writers

parser = argparse.ArgumentParser(description='Combine WebVTT segments spoken by the same person.')
parser.add_argument('input_file', type=str, help='path to input vtt file')
parser.add_argument('output_file', type=argparse.FileType('w', encoding='UTF-8'), help='path to desired output file, specify - for stdout')


def coalesce_vtt(input_file, output_file):

    speaker_max = 0
    speaker_pattern = re.compile(r'^\[SPEAKER_(?P<speaker_identifier>[0-9]+)\]: (?P<spoken_content>.*)$')

    vtt_input = list(webvtt.read(input_file))
    vtt_output = []
    
    for (index,subtitle) in enumerate(vtt_input):
        speaker_match = re.match(speaker_pattern, subtitle.text)
        if not speaker_match:
            # Speaker is unknown.
            # Since we cannot safely combine unknown speaker blocks, append and go to next.
            subtitle.text = f'[SPEAKER_UNKNOWN]: {subtitle.text}'
            vtt_output.append(subtitle)
            continue

        # we are sure speaker_match has both named groups
        speaker_num = int(speaker_match.group('speaker_identifier')) + 1
        speaker_identifier = f'{speaker_num:02}'
        if speaker_num > speaker_max:
            speaker_max = speaker_num
        spoken_content = speaker_match.group('spoken_content')
        subtitle.text = f'[SPEAKER_{speaker_identifier}]: {spoken_content}'

    
        # skip the first one
        if index == 1:
            vtt_output.append(subtitle)
            continue
        
        # Determine if this speaker is the same as the previous speaker
        #print(f'looking for match between {vtt_input[index-1].text} and {vtt_input[index].text}')
        previous_speaker_match = re.match(speaker_pattern, vtt_input[index-1].text)
        if previous_speaker_match and previous_speaker_match.group('speaker_identifier') == speaker_identifier:
            # they are the same. update the last element of vtt_output
            #   with the new ending timestamp and spoken content
            vtt_output[-1].end = subtitle.end
            vtt_output[-1].text += '\n' + spoken_content
    
        else:
            # they are not the same
            vtt_output.append(subtitle)
    
    print(webvtt.writers.webvtt_content(vtt_output), file=output_file)

if __name__ == '__main__':
    args = parser.parse_args()
    coalesce_vtt(args.input_file, args.output_file)
