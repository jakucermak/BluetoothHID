from blehidd import step_divider
import pytest

@pytest.mark.timeout(0.1)
class TestPosMoveDivider():
    

    def test_movement(self):
        current_step = 127
        current_relative_move = 200
        expected_result = 127

        result = step_divider(current_relative_move, current_step)

        assert expected_result == result

    def test_step_simple_rel_division(self):
        curr_step = 127
        curr_rel_move = 100

        expected_step = 64

        result = step_divider(curr_rel_move,curr_step)

        assert result == expected_step

    def test_step_multiple_rel_division(self):
       curr_step = 127
       curr_rel_move = 15

       expected_step = 8

       result = step_divider(curr_rel_move,curr_step)

       assert result == expected_step

    def test_step_multiple_until_one_point(self):
        curr_step = 127
        curr_rel_move = 1

        expected_step = 1

        result = step_divider(curr_rel_move, curr_step)

        assert result == expected_step


@pytest.mark.timeout(0.1)
class TestNegMoveDivider():

    def test_movement(self):
        curr_step = 128
        curr_relative_move = -200

        expected_step = 128
        
        result = step_divider(curr_relative_move, curr_step)
        
        assert result == expected_step

    def test_simple_step_division(self):
        curr_step = 128
        curr_relative_move = -127

        expected_step = 192

        result = step_divider(curr_relative_move, curr_step)
        assert result == expected_step

    def test_multiple_steps_division(self):
        curr_step = 128
        curr_relative_move = -15

        expected_step = 248

        result = step_divider(curr_relative_move, curr_step)

        assert result == expected_step
        
    def test_step_multiple_one_steps(self):
        curr_step = 127
        curr_rel_move = -2

        expected_step = 254

        result = step_divider(curr_rel_move, curr_step)

        assert result == expected_step 
    
    def test_multiple_step_division_until_1(self):
        curr_step = 128
        curr_relative_move = -1

        expected_step = 255

        result = step_divider(curr_relative_move, curr_step)

        assert result == expected_step


class TestCompareStepSizes():
    def test_simple_comparison(self):
        pos_step = 127
        neg_step = 128

        rel = 128

        pos_result = step_divider(rel,pos_step)
        neg_result = step_divider(rel * -1, neg_step)

        assert pos_result + 1 == neg_result

    def test_single_step_division(self):
        pos_step = 127
        neg_step = 128

        rel = 100

        pos = step_divider(rel, pos_step)
        neg = step_divider(rel * -1, neg_step)

        offset = 256

        assert pos == offset - neg

    def test_multiple_step_division(self):
        pos_step = 127
        neg_step = 128

        rel = 15
    
        pos = step_divider(rel, pos_step)
        neg = step_divider(rel * -1, neg_step)

        offset = 256
        
        assert pos == offset - neg

class TestWithSpeedChanges():
    
    def test_pos_with_simple_division_half_speed(self):
        step = 127
        rel = 200

        expected_step = 64
        result = step_divider(rel,step,0.5)

        assert result == expected_step

    def test_neg_with_simple_division_half_speed(self):
        step = 128
        rel = -200

        expected_step = 192
        result = step_divider(rel, step, 0.5)

        assert result == expected_step
