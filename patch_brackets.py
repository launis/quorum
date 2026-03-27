import re

def main():
    path = r"c:\src\quorum\client_app_v2\lib\features\studio\views\workflow_builder_view.dart"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    to_replace = """              }),
            ],
          ),
        ),
      ),
    ],
  ),
);
}"""

    replacement = """              }),
            ],
          ),
        ),
      ),
        ],
      ),
    ),
  );
}"""

    if to_replace in content:
        content = content.replace(to_replace, replacement)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print("Patched brackets.")
    else:
        print("Could not find the target string to replace.")

if __name__ == "__main__":
    main()
