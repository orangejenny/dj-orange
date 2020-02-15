// http://eslint.org/
module.exports = {
    "extends": "eslint:recommended",

    // http://eslint.org/docs/user-guide/configuring#specifying-environments
    "env": {
        "browser": true,
    },

    // http://eslint.org/docs/user-guide/configuring#specifying-globals
    "globals": {
        "assert": false,
        "d3": false,
    },

    // http://eslint.org/docs/rules/
    // http://eslint.org/docs/user-guide/configuring#configuring-rules
    "rules": {
        "brace-style": ["error", "1tbs"],
        "camelcase": ["error", {"properties": "never"}],
        "comma-dangle": ["warn", "always-multiline"],
        "curly": ["error"],
        "eqeqeq": ["error"],
        "func-call-spacing": ["error"],
        "indent": ["warn", 4, {"SwitchCase":1}],
        "linebreak-style": ["error", "unix"],
        "key-spacing": ["error"],
        "keyword-spacing": ["error"],
        "no-implicit-globals": ["error"],
        "no-irregular-whitespace": ["error"],
        "no-new-object": ["error"],
        "no-regex-spaces": ["error"],
        "no-throw-literal": ["error"],
        "no-unneeded-ternary": ["error"],
        "no-whitespace-before-property": ["error"], // match flake8 E201 and E211
        "one-var-declaration-per-line": ["error"],
        "semi": ["error", "always"],
        "space-before-function-paren": ["error", {"anonymous": "always", "named": "never", "asyncArrow": "always"}],
        "space-before-blocks": ["error"],
        "space-in-parens": ["error", "never"],
        "space-infix-ops": ["error"],   // match flake8 E225
    }
};
