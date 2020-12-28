<?php

error_reporting(E_ALL); // default (E_ALL)
set_time_limit(600); // 10min - default on php.ini = 36000secs

header('Content-Type: application/json');

require 'vendor/autoload.php';

use Goutte\Client as Goutte;
use GuzzleHttp\Client as Guzzle;

class Scrapping
{
	private Goutte $client;

	private string $city;
	private string $url;
	private int $timeout;
	private bool $pagination;

	public function __construct(String $city, bool $pagination, int $timeout = 3)
	{
		$this->city = strtoupper($city);
		$this->url = 'https://empresite.eleconomista.es/Actividad/' . $this->city . '/';
		$this->timeout = $timeout;
		$this->pagination = $pagination;

		$config = [
			'proxy' => [
				'185.110.96.11:3128',
				'185.110.96.12:3128'
			]
		];

		$this->client = new Goutte();
		$this->client->setHeader('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36');
		$this->client->setClient(new Guzzle($config));
	}

	public function pagination(array $pages): array
	{
		$pageNums = array();
		for ($i = 1; $i < sizeof($pages); $i++) {
			$pageNums[] = $pages[$i];
		}

		return $pageNums;
	}

	public function execute(): void
	{
		$crawler = $this->client->request('GET', $this->url);

		sleep($this->timeout);

		$hrefs = $crawler->filter('a[itemprop="url"]')->each(function ($node) {
			return $node->attr('href');
		});

		if ($this->pagination) {
			$pages = $crawler->filter('ul.pagination01>li')->each(function ($node) {
				return $node->text();
			});
			$pageNums = $this->pagination($pages);
			if (isset($pageNums) && !empty($pageNums)) {
				foreach ($pageNums as $key => $value) {
					$crawler = $this->client->request('GET', $this->url . 'PgNum-' . $value . '/');

					sleep($this->timeout);

					$temp = $crawler->filter('a[itemprop="url"]')->each(function ($node) {
						return $node->attr('href');
					});

					$hrefs = array_merge($hrefs, $temp);
				}
			}
		}

		$this->filter($hrefs);
	}

	public function filter(array $hrefs): void
	{
		$data = array();
		foreach ($hrefs as $key => $value) {
			$crawler = $this->client->request('GET', $value);

			$name = $crawler->filter('#datos-externos1>p.title02b')->each(function ($node) {
				return $node->text();
			});

			$email = $crawler->filter('span.email')->each(function ($node) {
				return $node->text();
			});

			$telephone = $crawler->filter('span[itemprop="telephone"]')->each(function ($node) {
				return $node->text();
			});

			sleep($this->timeout);

			$data[] = array(
				'name' => isset($name[0]) ? $name[0] : null,
				'email' => isset($email[0]) ? $email[0] : null,
				'phone' => isset($telephone[0]) ? $telephone[0] : null
			);

			$data = array_map('array_filter', $data);
			$data = array_filter($data);
		}
		echo json_encode($data);
	}
}

$scrap = new Scrapping("HOSPITAL", false);
$scrap->execute();
