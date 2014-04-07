package com.nr.test.servlet;

import java.io.IOException;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.sql.Statement;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public class DBServlet extends TestServlet {

    private Connection createConnection(String engine) throws Exception {
        if ("oracle".equals(engine)) {
            System.out.println("testing in Oracle");
            Class.forName("oracle.jdbc.driver.OracleDriver").newInstance();
            return DriverManager.getConnection("jdbc:oracle:thin:@172.16.1.87:1521:orcl", "system", "oracle");
        } else if ("postgres".equals(engine)) {
            System.out.println("testing in Postgres");
            Class.forName("org.postgresql.Driver").newInstance();
            return DriverManager.getConnection("jdbc:postgresql://172.16.2.236:5432/agent_test_pdql?user=agent_test&password=@gent!!!p");
        } else { // fall back to mysql
            System.out.println("testing in MySQL");

            Class.forName("com.mysql.jdbc.Driver").newInstance();
            return DriverManager.getConnection("jdbc:mysql://172.16.2.236/agent_test?user=agent_test&password=@g3nt!!!");
        }
    }

    private void runQuery(Connection con, String query) throws SQLException {
        Statement st = con.createStatement();
        ResultSet rs = st.executeQuery(query);
        ResultSetMetaData rmd = rs.getMetaData();

        int num_cols = rmd.getColumnCount();
        while (rs.next()) {
            for (int i = 1; i < num_cols; ++i) {
                rmd.getColumnName(i);
                rs.getString(i);
            }
            rmd.getColumnName(num_cols);
            rs.getString(num_cols);
        }
    }

    @Override
    protected void processRequest(HttpServletRequest req, HttpServletResponse resp) throws ServletException,
            IOException {

        String sql = req.getParameter("sql");
        String engine = req.getParameter("engine");

        System.out.println("processRequest: " + engine + ": " + sql);
        Connection con;
        try {
            con = createConnection(engine);
        } catch (Exception e) {
            e.printStackTrace(System.out);
            throw new RuntimeException(e);
        }

        try {
            runQuery(con, sql);
        } catch (Exception e) {
            e.printStackTrace(System.out);
            throw new RuntimeException(e);
        } finally {
            try {
                con.close();
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        }

        super.processRequest(req, resp);
    }

    @Override
    public String getServletInfo() {
        return "DB servlet";
    }
}
