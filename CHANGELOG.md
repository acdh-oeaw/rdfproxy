# Changelog

## [0.2.0](https://github.com/acdh-oeaw/rdfproxy/compare/v0.1.0...v0.2.0) (2024-12-23)


### Features

* expose SPARQLStrategies over library interface ([50270db](https://github.com/acdh-oeaw/rdfproxy/commit/50270db169ae03a47d3c3ba6c026ccc25a4bb50d))
* implement grouping by model field ([3d71409](https://github.com/acdh-oeaw/rdfproxy/commit/3d71409ad121578925e404bc624a2aba7d3284ba))
* implement model_bool hook for controlling model truthiness ([daf72cb](https://github.com/acdh-oeaw/rdfproxy/commit/daf72cb9e409aa750954ecee55b7d8c65f5f41a8))
* implement pagination behavior for grouped models ([386d990](https://github.com/acdh-oeaw/rdfproxy/commit/386d9902f28b6d6866cf51b606e0e4220812ce21))
* implement rdfproxy.ConfigDict extension for model configs ([f8a86b5](https://github.com/acdh-oeaw/rdfproxy/commit/f8a86b5b9268f2652e740220480b05010cfb6e16))
* implement strategies for SPARQL query functionality ([088509b](https://github.com/acdh-oeaw/rdfproxy/commit/088509b087984ab19357ec81a6bf76f6ebfe93ab))
* rewrite query construction functionality ([edb6fa0](https://github.com/acdh-oeaw/rdfproxy/commit/edb6fa0e078f58e5dd5c85e602b35e5d6982b5d3))
* use query parameter model for SPARQLModelAdapter.query ([72a273d](https://github.com/acdh-oeaw/rdfproxy/commit/72a273d028ee3271f3d39e6d3e43d65b95ec8516))


### Bug Fixes

* add type hints to revelen example route ([42ef1ce](https://github.com/acdh-oeaw/rdfproxy/commit/42ef1ce0d3288366854a776c66327e5ec71f9f36))
* correct regex pattern for SELECT clause extraction ([cb15e14](https://github.com/acdh-oeaw/rdfproxy/commit/cb15e1439c5446b2341c1217a5c724f59450179b))
* **get_items_query_constructor:** correct dict.get access ([3fc28b7](https://github.com/acdh-oeaw/rdfproxy/commit/3fc28b72674cc921a1b0ebac8926369c3da291a6))
* remove SPARQL prefixes from subqueries before query injections ([ecd70d7](https://github.com/acdh-oeaw/rdfproxy/commit/ecd70d7b8929f541a41f98ad7490af8573f3f29f))
* resolve group_by config values for SPARQL binding aliases ([5b3f171](https://github.com/acdh-oeaw/rdfproxy/commit/5b3f1711fe9f2aa0b50c890bce57c09728f6b5c9)), closes [#161](https://github.com/acdh-oeaw/rdfproxy/issues/161)


### Documentation

* adapt readme and examples to model field grouping ([b962af6](https://github.com/acdh-oeaw/rdfproxy/commit/b962af60402abaf6dc5486cca63d2bc9091d1fde))
* adapt readme and exmaples to rdfproxy.ConfigDict ([95a5b69](https://github.com/acdh-oeaw/rdfproxy/commit/95a5b69068de577761d8901c7bedd9152bfffeef))
* **examples:** adapt examples to query parameter model ([ebf5e0d](https://github.com/acdh-oeaw/rdfproxy/commit/ebf5e0dcf3f1af9c4d3571200fdb88faf73cbdd2))
* **examples:** update examples ([7146321](https://github.com/acdh-oeaw/rdfproxy/commit/7146321268c5b9a4d7ad345a8389ea906bc7d001))
* **readme:** adapt readme for query parameter model ([49a892c](https://github.com/acdh-oeaw/rdfproxy/commit/49a892c20d7d2a43e8fdf43443c3fd3ccc0a9371))
* **readme:** fix/improve example query ([318f630](https://github.com/acdh-oeaw/rdfproxy/commit/318f630d4c4685c51a6df83cc74b50c6f2b3df01))

## 0.1.0 (2024-10-23)


### Features

* Check for JSON result format to get_bindings_from_query_result ([f1a115a](https://github.com/acdh-oeaw/rdfproxy/commit/f1a115a779a41457d337e8d8397930f74ca16260))
* Expose more symbols over package interface ([d01fe29](https://github.com/acdh-oeaw/rdfproxy/commit/d01fe29277c0036ee236e437be592808151643a3)), closes [#11](https://github.com/acdh-oeaw/rdfproxy/issues/11)
* redesign SPARQLModelAdapter ([a386516](https://github.com/acdh-oeaw/rdfproxy/commit/a386516a5c9ee6faffbe0b285fe8fb08d05926ae))
* redesign SPARQLModelAdapter class ([48b3e27](https://github.com/acdh-oeaw/rdfproxy/commit/48b3e2776089c33ad6e0af97d0f366131b1b079c))
* Use conftest.py for global fixture definitions ([98f8933](https://github.com/acdh-oeaw/rdfproxy/commit/98f8933f1838c913575c4d6d3ad386e96db33140))


### Bug Fixes

* Adapt code to support 3.11 ([e053562](https://github.com/acdh-oeaw/rdfproxy/commit/e0535627361c907604d1c486540ecdc83be1aa42))
* adapt count query generator to correctly count grouped models ([affe933](https://github.com/acdh-oeaw/rdfproxy/commit/affe933f3332386285ddce0f47db6d0bd1d99e1a))
* **imports:** Remove unused imports flagged by Ruff ([0b1998f](https://github.com/acdh-oeaw/rdfproxy/commit/0b1998f838094ff38e0482f714776f3d7f5a4f7c))
* Type hint cleanup ([f4c0448](https://github.com/acdh-oeaw/rdfproxy/commit/f4c04487ba86699d41483a1f8fc8b47a01d2de08)), closes [#10](https://github.com/acdh-oeaw/rdfproxy/issues/10)


### Documentation

* Add author information to pyproject.toml ([bc3c2c9](https://github.com/acdh-oeaw/rdfproxy/commit/bc3c2c9ce4e5b5782eb0e916445935e1f831a2de))
* Add basic README ([95f423f](https://github.com/acdh-oeaw/rdfproxy/commit/95f423f3ececf9a933d6f2d7aeb9275a2f88e8cd))
* Add more info and example to SPARQLModelAdapter docstring ([59314b6](https://github.com/acdh-oeaw/rdfproxy/commit/59314b64a09aa8d98f8e73f22bcdde79ea1baa68))
* **examples:** initialize an examples section ([b5c6c13](https://github.com/acdh-oeaw/rdfproxy/commit/b5c6c137dfa16128c9f6eb902d33a06d853a8459))
* **readme:** replace wikidata query with VALUES query ([1c65983](https://github.com/acdh-oeaw/rdfproxy/commit/1c659834f3112b4af4fae8d7dff07025f9f9a50e))
* **readme:** update Python code examples to ConfigDict ([6cf5403](https://github.com/acdh-oeaw/rdfproxy/commit/6cf54037a057d5bfe6d54ff96dd718fb389eb4f4))
* **readme:** Update README.md ([a7c4525](https://github.com/acdh-oeaw/rdfproxy/commit/a7c4525d03ad2adb95ce9692956c8d3b6b8f2bce))
* Update README ([75c31fd](https://github.com/acdh-oeaw/rdfproxy/commit/75c31fdf943e4b5eaaec93cad996fa0b88de9400))
