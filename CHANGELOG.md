# Changelog

## [0.7.0](https://github.com/acdh-oeaw/rdfproxy/compare/v0.6.0...v0.7.0) (2025-06-12)


### Features

* implement detail view feature ([335045d](https://github.com/acdh-oeaw/rdfproxy/commit/335045dc623f0f69d09d0e9b8613ad4aff6f9538))
* make graph pattern injection optional in inject_into_query ([9671265](https://github.com/acdh-oeaw/rdfproxy/commit/967126569ce89af98d42186091270b4f9a7daead))
* make SPARQLWrapper/SPARQLModelAdapter asynchronous ([ee18122](https://github.com/acdh-oeaw/rdfproxy/commit/ee18122ac322cab6256c13206fa2ffe82c396208))
* update and publish RDFProxy exceptions ([642452f](https://github.com/acdh-oeaw/rdfproxy/commit/642452f92f6e545258eadff4b045751f8d204feb))


### Bug Fixes

* use OrderByEnum | None type for QueryParameters.order_by ([9eae9cb](https://github.com/acdh-oeaw/rdfproxy/commit/9eae9cb440330b45810da06352fd32fbb2d7eb11))


### Documentation

* add detail routes to full_static_fastapi_example ([32ee3df](https://github.com/acdh-oeaw/rdfproxy/commit/32ee3df30da7661f2a0468fd2c62652de1425c41))

## [0.6.0](https://github.com/acdh-oeaw/rdfproxy/compare/v0.5.1...v0.6.0) (2025-04-16)


### Features

* implement public ModelBindingsMapper subclass ([df1894b](https://github.com/acdh-oeaw/rdfproxy/commit/df1894b697a77a22cfed97e69cdd0906c2abb341))
* support rdflib.Graph as a SPARQL target ([b9a53c7](https://github.com/acdh-oeaw/rdfproxy/commit/b9a53c76ee9dc37da956a33a9fe23b6035e345d5))


### Bug Fixes

* add order by solution modifier for outer query ([bdb47e5](https://github.com/acdh-oeaw/rdfproxy/commit/bdb47e5b05d1f70e34ceb2e6be1ad60704d22314))
* handle empty SPARQL bindings/dataframes in mapper ([4e31e4a](https://github.com/acdh-oeaw/rdfproxy/commit/4e31e4a24c749e916a7c3394f3cf47f7c15cc6dd))
* handle None-valued group keys correctly in mapper aggregation ([8bc260a](https://github.com/acdh-oeaw/rdfproxy/commit/8bc260ab4ccf6d1b981a5d1532dfebddd9d73aa8))


### Documentation

* refine model_traverse function doc string ([9be52fd](https://github.com/acdh-oeaw/rdfproxy/commit/9be52fdefa922ebb91c3b5a3403c16fc4c2bacc2))

## [0.5.1](https://github.com/acdh-oeaw/rdfproxy/compare/v0.5.0...v0.5.1) (2025-04-02)


### Bug Fixes

* use token env var ([409554c](https://github.com/acdh-oeaw/rdfproxy/commit/409554c51bc1152c305164e843b977b3e45b2961))

## [0.5.0](https://github.com/acdh-oeaw/rdfproxy/compare/v0.4.1...v0.5.0) (2025-04-02)


### Features

* raise HTTP status in SPARQLWrapper.query ([c9fb82b](https://github.com/acdh-oeaw/rdfproxy/commit/c9fb82b632318d8e6582ed319b1b73562112f9f0))

## [0.4.1](https://github.com/acdh-oeaw/rdfproxy/compare/v0.4.0...v0.4.1) (2025-04-01)


### Bug Fixes

* correct yaml syntax in publish action ([b195a39](https://github.com/acdh-oeaw/rdfproxy/commit/b195a391b8c1029cce2a15e2543cb061a82d43f2))

## [0.4.0](https://github.com/acdh-oeaw/rdfproxy/compare/v0.3.0...v0.4.0) (2025-04-01)


### Features

* add checker for union model type fields ([b066986](https://github.com/acdh-oeaw/rdfproxy/commit/b066986ee6f338b738e4ebdb3239d55ae4cb65ee))
* add consume function ([7bb3d12](https://github.com/acdh-oeaw/rdfproxy/commit/7bb3d1202aeeccdb0c940e5447214a3f876e56fe))
* add mapper code paths for handling union models ([c1c2ea4](https://github.com/acdh-oeaw/rdfproxy/commit/c1c2ea46446a2edc95d93b60987df925d2e39c2d))
* allow traversal of union models in model_traverse ([217fed7](https://github.com/acdh-oeaw/rdfproxy/commit/217fed7713c3c59f1feef0bc4c97cb93ad9bd425))
* implement model_bool check for sub models ([df91d1d](https://github.com/acdh-oeaw/rdfproxy/commit/df91d1db717311085dcd38f53549525a4de34520))
* refactor model checking and add model_bool root model check ([3350739](https://github.com/acdh-oeaw/rdfproxy/commit/3350739f49096cc3a7bdb50d911f7d96ef658fd1))


### Bug Fixes

* allow set[str] instead of arbitrary Iterables for model_bool ([87cee36](https://github.com/acdh-oeaw/rdfproxy/commit/87cee361da67f5ea214b0804c168ea4b64687b35))
* check for types.UnionType AND typing.Union ([433224d](https://github.com/acdh-oeaw/rdfproxy/commit/433224d2e3ff8f833cb01ac68e07812cb169d0d0))


### Documentation

* **examples:** add example of model_bool for union models ([7fe4f6c](https://github.com/acdh-oeaw/rdfproxy/commit/7fe4f6c9d8c864deb4578c313427ed6c98a05744))

## [0.3.0](https://github.com/acdh-oeaw/rdfproxy/compare/v0.2.0...v0.3.0) (2025-03-18)


### Features

* add __init__ for rdfproxy.utils ([99cd75d](https://github.com/acdh-oeaw/rdfproxy/commit/99cd75d3b2382e028e654b218c2df068344c54f8))
* add order_by and desc fields to QueryParameters model ([b0a6e2c](https://github.com/acdh-oeaw/rdfproxy/commit/b0a6e2c4e1c79e72eeb4dd656c184579c39799fe))
* add QueryParameters default argument ([88cdcfb](https://github.com/acdh-oeaw/rdfproxy/commit/88cdcfbcdbce21d874ad88cbe907cec840c1b7e9))
* change _ModelBindingsMapper bindings param to take an Iterable ([b06eb36](https://github.com/acdh-oeaw/rdfproxy/commit/b06eb36cfa2497b5b651ccaf39f1f38fed555bfd))
* implement basic logging for SPARQLModelAdapter ([dd2a1b3](https://github.com/acdh-oeaw/rdfproxy/commit/dd2a1b37a3a66d6dde92455f056191a56ee8a478))
* implement generic model traversal function ([858657c](https://github.com/acdh-oeaw/rdfproxy/commit/858657c36dc3e50188cbe76c35effc3d38870da4))
* implement model checking ([07669cb](https://github.com/acdh-oeaw/rdfproxy/commit/07669cb8da67163bb0cd703919d34a68b70634f2))
* implement order_by value injection in _QueryConstructor ([bae2c1f](https://github.com/acdh-oeaw/rdfproxy/commit/bae2c1fd1f8b965e660a90aef0238d5409f93eb6))
* implement OrderableFieldsBindingsMap ([eab26d3](https://github.com/acdh-oeaw/rdfproxy/commit/eab26d338743486b4406cdac80bb955d632baa9c))
* implement query checking ([d25b5af](https://github.com/acdh-oeaw/rdfproxy/commit/d25b5afee9c4954a6d6102e9e60938ca6d8b5a57))
* implement thin httpx SPARQLWrapper ([800ddec](https://github.com/acdh-oeaw/rdfproxy/commit/800ddec18fcda93485d12faf29e6d582366e3718))
* implement toPyton workaround for xsd:gYear/xsd:gYearMonth ([87fc55d](https://github.com/acdh-oeaw/rdfproxy/commit/87fc55db367ee0c1cbbcf9c4c946d503e08c1c30))
* introduce rdfproxy.utils._typing module ([981eea3](https://github.com/acdh-oeaw/rdfproxy/commit/981eea3066e94814995cee9f3383c280a189748f))
* mark QueryConstructor class private ([4769423](https://github.com/acdh-oeaw/rdfproxy/commit/4769423888882d7925532c3efdf396ffb5e88f22))
* **SPARQLWrapper:** implement RDFLib-based response extraction ([17b3693](https://github.com/acdh-oeaw/rdfproxy/commit/17b3693eef327196a16b4c72381281e7221277d1))


### Bug Fixes

* adapt types in full_static_model_fastapi_example.py ([2689b32](https://github.com/acdh-oeaw/rdfproxy/commit/2689b32dc0900ef191f9391a0b2c8115024fa3f6))
* correct pre-commit yaml and deactivate hooks ([08c8e07](https://github.com/acdh-oeaw/rdfproxy/commit/08c8e07b5be1ab8811ea0c07d9e58477ebebb6e7))
* **docs:** use correct link to tests badge ([65b5abb](https://github.com/acdh-oeaw/rdfproxy/commit/65b5abb2bfb8eda3342e6cc0966f5bdf901553c9))
* handle all-UNDEF binding aggregation ([9be99ba](https://github.com/acdh-oeaw/rdfproxy/commit/9be99ba8a4d84818428de21197aaf739db23ecbe))
* initialize pd.DataFrame with arbitrary Python types ([bd3522b](https://github.com/acdh-oeaw/rdfproxy/commit/bd3522b6f134389df573646835bf91f391ba0e81))
* **logging:** use % format specifier for logging ([b1ea529](https://github.com/acdh-oeaw/rdfproxy/commit/b1ea5294dfee823aec6ebcc68d33b60e2bedcc1a))
* reference private _QueryConstructor correctly in mkdocs ([1968eb7](https://github.com/acdh-oeaw/rdfproxy/commit/1968eb7fb1994f77fa24ad5b78f1679142263862))
* require SPARQL variable marker in add_solution_modifier ([1f122c1](https://github.com/acdh-oeaw/rdfproxy/commit/1f122c19769ab8067b7e50a8c5c55d59f0194427))
* **test:** adapt SPARQL bindings to match model fields ([90a6a9a](https://github.com/acdh-oeaw/rdfproxy/commit/90a6a9a6790cf07fc5361a4509cbb516d98756e7))
* **test:** fix sketchy test for ModelBindingsMapper ([6ba1e49](https://github.com/acdh-oeaw/rdfproxy/commit/6ba1e493b292fb17ce849af4170cde4bc1325499))
* **test:** use actual models for Page.items in test parameters ([e117388](https://github.com/acdh-oeaw/rdfproxy/commit/e11738841af84e52d2fa1b8d6bcda0b786cc22a7))


### Documentation

* adapt examples to parametrized Queryparameters model feature ([b15a316](https://github.com/acdh-oeaw/rdfproxy/commit/b15a316b3f3b57e5f6c6728a405e0b2baa29cf89))
* correct minor typo in docstring ([7ba2772](https://github.com/acdh-oeaw/rdfproxy/commit/7ba2772581b3a1341a728d3b4a0185f013110fc4))
* **readme:** add docs status badge to readme ([4d15e06](https://github.com/acdh-oeaw/rdfproxy/commit/4d15e06c62271af9ebd3fd366bbf72ef4a6bc87a))
* setup basic mkdocs ([2b1dba2](https://github.com/acdh-oeaw/rdfproxy/commit/2b1dba2ab097a4fdbcefe11bc390aadc9975304d))
* update examples README ([686864e](https://github.com/acdh-oeaw/rdfproxy/commit/686864e185736fbd6aa3fa81e90c69513714549b))

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
