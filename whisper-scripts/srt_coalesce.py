import argparse
import re

import srt

parser = argparse.ArgumentParser(description='Combine SRT segments spoken by the same person.')
parser.add_argument('input_file', type=open, help='path to input srt file')
parser.add_argument('output_file', type=argparse.FileType('w', encoding='UTF-8'), help='path to desired output file, specify - for stdout')


def coalesce_srt(input_file, output_file):

    speaker_max = 0
    speaker_pattern = re.compile(r'^\[SPEAKER_(?P<speaker_identifier>[0-9]+)\]: (?P<spoken_content>.*)$')

    srt_input = list(srt.parse(input_file))
    srt_output = []
    
    for (index,subtitle) in enumerate(srt_input):
        speaker_match = re.match(speaker_pattern, subtitle.content)
        if not speaker_match:
            # Speaker is unknown.
            # Since we cannot safely combine unknown speaker blocks, append and go to next.
            subtitle.content = f'[SPEAKER_UNKNOWN]: {subtitle.content}'
            srt_output.append(subtitle)
            continue

        # we are sure speaker_match has both named groups
        speaker_num = int(speaker_match.group('speaker_identifier')) + 1
        if speaker_num > speaker_max:
            speaker_max = speaker_num
        speaker_identifier = speaker_match.group('speaker_identifier')
        spoken_content = speaker_match.group('spoken_content')

    
        # skip the first one
        if subtitle.index == 1:
            srt_output.append(subtitle)
            continue
        
        # Determine if this speaker is the same as the previous speaker
        #print(f'looking for match between {srt_input[index-1].content} and {srt_input[index].content}')
        previous_speaker_match = re.match(speaker_pattern, srt_input[index-1].content)
        if previous_speaker_match and previous_speaker_match.group('speaker_identifier') == speaker_match.group('speaker_identifier'):
            # they are the same. update the last element of srt_output
            #   with the new ending timestamp and spoken content
            srt_output[-1].end = subtitle.end
            srt_output[-1].content += '\n' + speaker_match.group('spoken_content')
    
        else:
            # they are not the same
            srt_output.append(subtitle)
    
    print(srt.compose(srt_output), file=output_file)

if __name__ == '__main__':
    args = parser.parse_args()
    coalesce_srt(args.input_file, args.output_file)
