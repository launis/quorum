import os
import re

TEST_DIR = "backend_v2/tests"

ID_PATTERNS = [
    (r'wf_valid[a-zA-Z0-9_]*', 'wf_1111111111111111'),
    (r'wf_new[a-zA-Z0-9_]*', 'wf_2222222222222222'),
    (r'wf_clone[a-zA-Z0-9_]*', 'wf_3333333333333333'),
    (r'wf_tgtest[a-zA-Z0-9_]*', 'wf_4444444444444444'),
    (r'wf_testwf[a-zA-Z0-9_]*', 'wf_5555555555555555'),
    
    (r'blk_steproot[a-zA-Z0-9_]*', 'blk_aaaa1111bbbb2222'),
    (r'blk_stepleaf[a-zA-Z0-9_]*', 'blk_cccc3333dddd4444'),
    (r'blk_aaaa[a-zA-Z0-9_]*', 'blk_aaaa111111111111'),
    (r'blk_bbbb[a-zA-Z0-9_]*', 'blk_bbbb222222222222'),
    (r'blk_cccc[a-zA-Z0-9_]*', 'blk_cccc333333333333'),
    (r'blk_step1234', 'blk_dddd4444dddd4444'),
    (r'blk_validblock', 'blk_eeee5555eeee5555'),
    (r'blk_mockpb[a-zA-Z0-9_]*', 'blk_ffff6666ffff6666'),

    (r'exe_1234abcd', 'exe_1111111122222222'),
    (r'exe_abcdefgh123', 'exe_aaaaaaaabbbbbbbb'),
    (r'exe_test0000test001', 'exe_0000000000000001'),
    (r'exe_test0000test002', 'exe_0000000000000002'),
    (r'exe_testexec123', 'exe_eeeeeeeeeeeeeeee'),

    (r'step_blueprint', 'step_11111111bbbbbbbb'),
    (r'step_11111111', 'step_1111111111111111'),
    (r'step_fail11111', 'step_ffff1111ffff1111'),
    (r'step_sleep2222', 'step_5555222255552222'),
    
    (r'prof_mock123', 'prof_mmmm1111mmmm1111'),
    (r'prof_defaultmock123', 'prof_dddd1111dddd1111'),
    
    (r'legacy-slug-without-prefix', 'org_1234567890123456'), # Just needs to fail parsing, or maybe keep as is to test failure
    (r"'^\(\[a-z\]\{2,5\}\)_\[a-zA-Z0-9\]\{8,\}\$'", r"'^([a-z]{2,5})_[a-fA-F0-9]{16,32}$'"),
]

def fix_tests():
    fixed_count = 0
    for root, _, files in os.walk(TEST_DIR):
        for file in files:
            if not file.endswith(".py"):
                continue
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            original = content
            for pattern, replacement in ID_PATTERNS:
                content = re.sub(pattern, replacement, content)

            if content != original:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                fixed_count += 1
                print(f"Fixed: {path}")

    print(f"Total files fixed: {fixed_count}")

if __name__ == "__main__":
    fix_tests()
