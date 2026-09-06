<?php
/**
 * Dedicated table for locally-cached asset/rights metadata.
 *
 * Decision (Phase 2, per the source plan's suggestion for high-volume
 * records): `smashfire_pr_asset` is a custom table, not a CPT — media
 * count per submission can be large and none of it needs a native post
 * editor screen. The Hub's own `assets` table (see the Hub data model in
 * docs/Smashfire_PR_Full_Product_Technical_Plan_2026.md) remains the
 * canonical, multi-tenant record; this table is only ever a local cache
 * keyed to a `smashfire_pr_submission` post.
 *
 * Schema is created now, before any code reads or writes it, so the
 * decision is locked in structurally rather than retrofitted once real
 * asset handling lands — the same reasoning the Hub's Phase 1 migration
 * used for `publisher_id`.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

class Smashfire_PR_Asset_Table {

	public static function table_name(): string {
		global $wpdb;
		return $wpdb->prefix . 'smashfire_pr_assets';
	}

	public static function register_activation_hook( string $plugin_file ): void {
		register_activation_hook( $plugin_file, array( __CLASS__, 'create_table' ) );
	}

	public static function create_table(): void {
		global $wpdb;

		$table_name      = self::table_name();
		$charset_collate = $wpdb->get_charset_collate();

		$sql = "CREATE TABLE {$table_name} (
			id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
			submission_post_id BIGINT UNSIGNED NOT NULL,
			hub_asset_id VARCHAR(64) DEFAULT NULL,
			type VARCHAR(32) NOT NULL,
			mime_type VARCHAR(128) DEFAULT NULL,
			credit VARCHAR(255) DEFAULT NULL,
			rights_status VARCHAR(32) NOT NULL DEFAULT 'pending',
			created_at DATETIME NOT NULL,
			PRIMARY KEY  (id),
			KEY submission_post_id (submission_post_id)
		) {$charset_collate};";

		require_once ABSPATH . 'wp-admin/includes/upgrade.php';
		dbDelta( $sql );
	}
}
